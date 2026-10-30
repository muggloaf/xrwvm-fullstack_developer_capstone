# Remaining submission evidence

Evidence must come from the running services and browser. This checklist is not
a substitute for a screenshot, a deployment URL, or a successful workflow log.

| Question | Required artifact |
| --- | --- |
| 9 | `getalldealers`: cURL and response from `/fetchDealers` |
| 10 | `getdealerbyid`: cURL and response from `/fetchDealer/1` |
| 11 | `getdealersbyState`: cURL and response from `/fetchDealers/Kansas` |
| 12 | `admin_login.png`: authenticated Django superuser page |
| 13 | `admin_logout.png`: logged-out Django admin page |
| 14 | `getallcarmakes`: cURL and response from `/djangoapp/get_cars` |
| 15 | `analyzereview`: cURL and response from the Code Engine sentiment URL |
| 16 | `get_dealers.png`: dealer list before login |
| 17 | `get_dealers_loggedin.png`: dealer list with username and Review Dealer |
| 18 | `dealersbystate.png`: list filtered to Kansas |
| 19 | `dealer_id_reviews.png`: dealer 15 with its seeded reviews |
| 20 | `dealership_review_submission.png`: filled review form before submission |
| 21 | `added_review.png`: posted review with its sentiment |
| 22 | `CI-CD.txt`: complete successful GitHub Actions run output |
| 23 | `deploymentURL`: actual lab Kubernetes application URL |
| 24 | `deployed_landingpage.png`: deployed landing page |
| 25 | `deployed_loggedin.png`: deployed application with username |
| 26 | `deployed_dealer_detail.png`: deployed dealer and reviews |
| 27 | `deployed_add_review.png`: new review in the deployed application |

Keep the real browser address bar visible in screenshots. Use the same lab
deployment URL for Questions 23–27. Local Docker execution is useful for testing,
but does not establish deployment to the Skills Network Kubernetes cluster.

## Run locally

1. Start the backend with `docker compose -f server/database/docker-compose.yml up --build -d`.
2. Build the sentiment service with `docker build -t capstone-sentiment server/djangoapp/microservices`.
3. Run it on the backend Docker network, exposing container port 5000 as local port 5050.
4. Build the complete application with `docker build -t capstone-dealership server`.
   The multi-stage Dockerfile builds React automatically.
5. Run the application on the same network with `backend_url=http://api:3030`
   and `sentiment_analyzer_url=http://capstone-sentiment:5000`.

## Lab deployment

`scripts/deploy_lab.sh` uses the authenticated Skills Network CLI environment.
It requires the lab's `SN_ICR_NAMESPACE` and the running Express service's
`BACKEND_URL`. It builds and pushes the sentiment and Django images, deploys the
sentiment service on Code Engine, and rolls out Django on Kubernetes. It does not
delete existing deployments, images, or user data.

The repository's `server/deployment.yaml` contains explicit placeholders until
the real lab namespace and Code Engine URL are available.
