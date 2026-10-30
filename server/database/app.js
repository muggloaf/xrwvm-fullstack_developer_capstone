/*jshint esversion: 8 */
const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const path = require('path');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const app = express();
const port = process.env.PORT || 3030;

// Rate limiter for fetching a single dealer by ID
const fetchDealerLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs for this endpoint
});

app.use(cors());
app.use(require('body-parser').urlencoded({ extended: false }));

const reviews_data = JSON.parse(fs.readFileSync(path.join(__dirname, 'data/reviews.json'), 'utf8'));
const dealerships_data = JSON.parse(fs.readFileSync(path.join(__dirname, 'data/dealerships.json'), 'utf8'));

const reviewLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs for review insertion
  standardHeaders: true,
  legacyHeaders: false,
});

const fetchDealersLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 200, // limit each IP to 200 requests per windowMs for fetching dealers
  standardHeaders: true,
  legacyHeaders: false,
});

const fetchReviewsByDealerLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 200, // limit each IP to 200 requests per windowMs for fetching reviews by dealer
  standardHeaders: true,
  legacyHeaders: false,
});

const fetchAllReviewsLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 200, // limit each IP to 200 requests per windowMs for fetching all reviews
  standardHeaders: true,
  legacyHeaders: false,
});

const Reviews = require('./review');

const Dealerships = require('./dealership');

// Seed only an empty database. Restarting must preserve submitted reviews.
async function start() {
  await mongoose.connect(process.env.MONGO_URL || 'mongodb://mongo_db:27017/', {
    dbName: 'dealershipsDB',
  });
  if (await Reviews.countDocuments() === 0) {
    await Reviews.insertMany(reviews_data.reviews);
  }
  if (await Dealerships.countDocuments() === 0) {
    await Dealerships.insertMany(dealerships_data.dealerships);
  }
  app.listen(port, () => console.log(`Server is running on port ${port}`));
}


// Express route to home
app.get('/', async (req, res) => {
    res.send("Welcome to the Mongoose API");
});

// Express route to fetch all reviews
app.get('/fetchReviews', fetchAllReviewsLimiter, async (req, res) => {
  try {
    const documents = await Reviews.find();
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Express route to fetch reviews by a particular dealer
app.get('/fetchReviews/dealer/:id', fetchReviewsByDealerLimiter, async (req, res) => {
  try {
    const documents = await Reviews.find({dealership: req.params.id});
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Express route to fetch all dealerships
app.get('/fetchDealers', fetchDealersLimiter, async (req, res) => {
  try {
    const documents = await Dealerships.find();
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Express route to fetch Dealers by a particular state
app.get('/fetchDealers/:state', fetchDealersLimiter, async (req, res) => {
  try {
    const documents = await Dealerships.find({state: req.params.state});
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Express route to fetch dealer by a particular id
app.get('/fetchDealer/:id', fetchDealerLimiter, async (req, res) => {
  try {
    const documents = await Dealerships.find({id: req.params.id});
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

//Express route to insert review
app.post('/insert_review', reviewLimiter, express.json(), async (req, res) => {
  try {
    const data = req.body;
    const latest = await Reviews.findOne().sort({ id: -1 });
    const new_id = latest ? latest.id + 1 : 1;
    const review = new Reviews({
		"id": new_id,
		"name": data.name,
		"dealership": data.dealership,
		"review": data.review,
		"purchase": data.purchase,
		"purchase_date": data.purchase_date,
		"car_make": data.car_make,
		"car_model": data.car_model,
		"car_year": data.car_year,
	});

    const savedReview = await review.save();
    res.json(savedReview);
  } catch (error) {
		console.log(error);
    res.status(500).json({ error: 'Error inserting review' });
  }
});

// Do not accept requests until MongoDB and seed data are ready.
start().catch(error => {
  console.error('Failed to start dealership API:', error.message);
  process.exitCode = 1;
});
