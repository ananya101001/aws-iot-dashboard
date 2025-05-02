# Serverless IoT Sensor Analytics on AWS

This project demonstrates a simple, functional serverless cloud application on AWS that simulates IoT sensor data, ingests it securely, performs basic real-time analytics, and displays the results on a simple web dashboard. It integrates core cloud concepts like serverless architecture, IoT communication, and data handling.

## Architecture

The application uses the following AWS services in a serverless pattern:


Features
Simulated IoT Sensors: A Python script simulates two sensors (e.g., temperature and humidity) generating data streams.
Secure Data Ingestion: Uses MQTT protocol with certificate-based authentication via AWS IoT Core.
Serverless Data Processing: AWS Lambda functions handle data ingestion logic (via IoT Rule) and analytics calculations.
Persistent Storage: Amazon DynamoDB stores both raw sensor readings and calculated analytics results.
Scheduled Analytics: A CloudWatch Scheduled Event triggers a Lambda function periodically (e.g., every minute) to calculate basic analytics (Average, Min, Max) over a recent time window.
Real-time Dashboard: A simple HTML/JavaScript dashboard fetches the latest readings and analytics via Amazon API Gateway and updates automatically.


Technology Stack
Cloud Provider: AWS (Amazon Web Services)
IoT: AWS IoT Core (MQTT Broker, Rules Engine, Device Management)
Compute: AWS Lambda (Python 3.x)
Database: Amazon DynamoDB (NoSQL Key-Value & Document Database)
API: Amazon API Gateway (REST API)
Orchestration/Scheduling: Amazon EventBridge (CloudWatch Events)
Languages/SDK: Python 3.x, Boto3 (AWS SDK for Python), AWSIoTPythonSDK, HTML, JavaScript


Prerequisites
Before you begin, ensure you have the following:
AWS Account: An active AWS account with permissions to create/manage IoT Core, Lambda, DynamoDB, API Gateway, EventBridge, and IAM resources.
AWS Credentials: Configure your AWS credentials locally so that scripts and the AWS CLI/SDK can interact with your account. This is typically done via environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION) or the ~/.aws/credentials file. See AWS Configuration Basics.
Python 3.x: Installed on your local machine.
Pip: Python package installer (usually comes with Python 3).
Git: Installed on your local machine.
AWS IoT Certificates: You will need to create an IoT Thing in AWS and download the corresponding certificate files (.crt, .key, root CA .pem). These files are sensitive and should NOT be committed to Git. Keep them secure locally.


Setup and Installation
Clone Repository:
git clone https://github.com/ananya101001/aws-iot-dashboard
cd YourRepositoryName


# pip install AWSIoTPythonSDK boto3
Use code with caution.

Create AWS Resources:
DynamoDB Tables:
Create table RawSensorData (Partition Key: deviceID (String), Sort Key: timestamp (Number)).
Create table SensorAnalytics (Partition Key: sensorType (String)).
AWS IoT Core:
Create an IoT "Thing" (e.g., MySimulatedDevice).
Create a new Certificate and download all files (Device certificate .crt, Private key .key, Root CA .pem - e.g., Amazon Root CA 1). Activate the certificate. Store these securely.
Create an IoT Policy (like MyDevicePolicy) allowing iot:Connect (for your specific client ID/Thing ARN) and iot:Publish (to topic sensors/data). Attach this policy to the certificate you created.
Note your AWS IoT Core Endpoint from the Settings page.
IoT Rule:
Create an IoT Rule (StoreSensorDataRule).
Rule query statement: SELECT * FROM 'sensors/data'
Action: Send message data to DynamoDB table RawSensorData. Map partitionKey=${deviceId} and sortKey=${timestamp}. Create a new IAM Role (IoTRuleToDynamoDBRole) when prompted to allow this action.
IAM Role for Lambdas:
Create an IAM Role (LambdaDynamoDBAccessRole) for Lambda execution.
Trust relationship: Lambda service (lambda.amazonaws.com).
Permissions: Attach policies like AWSLambdaBasicExecutionRole (for logs) and grant permissions to read/write to both RawSensorData and SensorAnalytics DynamoDB tables (e.g., AmazonDynamoDBFullAccess for simplicity, or a more restricted custom policy).
Lambda Functions:
Create CalculateSensorAnalytics function (Python 3.x runtime). Upload code from src/lambda/calculate_analytics/lambda_function.py. Assign the LambdaDynamoDBAccessRole. Increase the timeout (e.g., to 30 seconds).
Create GetSensorDataForDashboard function (Python 3.x runtime). Upload code from src/lambda/get_dashboard_data/lambda_function.py. Assign the LambdaDynamoDBAccessRole.
CloudWatch Event Rule (EventBridge):
Create a scheduled rule (RunAnalyticsEveryMinute).
Define pattern: Schedule, Fixed rate of 1 minute.
Target: Select the CalculateSensorAnalytics Lambda function.
API Gateway:
Create a new REST API (SensorDataAPI).
Create a resource /data.
Create a GET method for /data.
Integration type: Lambda Function, check "Use Lambda Proxy integration". Select the GetSensorDataForDashboard function.
Enable CORS on the /data resource and/or the GET method.
Deploy the API to a stage (e.g., prod).
Note the Invoke URL of the deployed stage.
Configure Local Files:
Simulator (simulator/sensor_simulator.py):
Update AWS_IOT_ENDPOINT with your IoT Core endpoint.
Update PATH_TO_CERT, PATH_TO_KEY, PATH_TO_ROOT_CA to point to the actual paths where you securely stored your downloaded IoT certificates.
Ensure CLIENT_ID matches the Thing name or Client ID allowed in your IoT Policy.
Dashboard (dashboard/dashboard.html):
Update const apiUrl with the Invoke URL you got after deploying the API Gateway stage.
Running the Application
Start the Simulator:
Open a terminal, navigate to the project directory, and run:
python simulator/sensor_simulator.py
Use code with caution.
Bash
You should see "Published..." messages indicating data is being sent to AWS IoT Core.
View the Dashboard:
Open the dashboard/dashboard.html file in your web browser.
The "Latest Sensor Readings" section should update shortly after the simulator starts sending data.
The "Real-Time Analytics" section will populate/update approximately every minute after the analytics Lambda runs. (It may take a minute or two for the first calculation).
Project Structure
.
├── simulator/
│   └── sensor_simulator.py       # Simulates IoT sensors and sends data
├── src/
│   └── lambda/
│       ├── calculate_analytics/
│       │   └── lambda_function.py  # Lambda for calculating analytics
│       └── get_dashboard_data/
│           └── lambda_function.py  # Lambda serving data to the dashboard
├── dashboard/
│   └── dashboard.html            # Simple web dashboard
├── docs/
│   └── architecture.md           # Contains Mermaid diagram source (optional)
├── .gitignore                    # Specifies intentionally untracked files
├── README.md                     # This file
└── requirements.txt              # Python dependencies (optional but recommended)



