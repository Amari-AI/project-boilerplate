# Project Components (Requirements)

In this project, you’ll have to develop a production-ready application that takes in shipment
documents and extracts data for the user.

This is for an interview assessment for useanchor.ai. Look them up online if more context is needed to complete the task

## API

Create an API that takes in a list of document files and extracts relevant data. There can be
multiple documents (PDFs and/or XLSX) related to a single shipment

This will be a python fastapi application that will be called by the front-end.

BE AWARE: There may be multiple issues in the current boilerplate.

Documents
For testing, you’ll be given two documents:
● A bill of lading (.pdf)
● A commercial invoice and packing list (.xlxs)

## UI

Create a platform with the following functionalities:
1. Upload the documents to extract data.
2. show an editable form with prefilled data:
    Bill of lading number
    Container number
    Consignee Name
    Consignee Address
    Date
    Line Items Count
    Average Gross Weight
    Average Price
3. Option to view the documents on the side with the extracted data for easy audit

This will be a next.js application. It will call the python api to extract the data and display it in a form.

# Bonus Work

## Deployment

Make the application production-ready by containerizing it with Docker.
Include all dependencies and setup network between the containers (the python api and the next.js app)


## Evaluation

Come up with an eval script that calculates accuracy, precision, 
recall, and F1 for the given set of documents. This will help us understand how robust the product is.

## Testing

Write unit tests for the functions to verify the API. You can use pytest library for the unit tests.

# Agents

This work will be split up amongst multiple agents.

## Agent 1

You are in charge of the python API. Your job is to verify the base API which scrapes the text 
from the documents entered and verify that the output is correct. Fix any bugs in the code.

## Agent 2

You are in charge of the next.js app. You will create the UI for the app. You will also create the 
form that displays the data extracted from the documents. You will also create the view that displays 
the documents on the side with the extracted data for easy audit.

### UX Flow

1. User uploads documents
2. User clicks on "Extract Data"
3. User is shown a form with prefilled data
4. User can edit the data
5. User can view the documents on the side with the extracted data for easy audit

## Agent 3

You are in charge of the evaluation script. You will create a script that calculates accuracy, 
precision, recall, and F1 for the given set of documents. This will help us understand how robust 
the product is.

## Agent 4

You are in charge of the deployment. You will containerize the application with Docker. You will 
also setup the network between the containers (the python api and the next.js app)

## Agent 5

You are in charge of the unit tests. You will write unit tests for the functions to verify the API. 
You can use pytest library for the unit tests.
