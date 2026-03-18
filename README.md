# 3PO
Parallel Post Positivity Observer

## 1) Introduction  
The top level product of this pipeline is a timeseries of 'positivity' across multiple platforms; by running sentiment analysis on the most popular posts, and weighting them based on approximation of impressions. The system also stores several other tables and files, that were part of the pipeline, or otherwise provide more clarity about the posts or the system. These will be listed in section 3. The code is currently set up to track the social media platforms Bluesky and Mastodon, but the system is made to be expandable, only requiring changes in the Ingestion notebook [link]. Early versions tracked Reddit as well, but the endpoint was not open to Databricks.

## 2) Completed tasks  
In short, this project includes all tasks with the exception of 'Structured logging & error handling'. As per the instructions, completed tasks will be listed here. How these were implemented will be described batchwise in section 6, by which the structure of the project should be clearer. Description of solution with illustrative elements. Data schema description and pipeline description.  
Repository organization & documentation  
Overall presentation & language  
Scope & innovativeness, originality  
Structured data (batch/manual)  
Unstructured data (batch/manual)  
Real-time or automated batch ingestion  
Implement ETL to clean, transform, and standardize data  
Apply data deduplication & type validation, basic metadata  
Advanced/automated metadata (e.g., profiling, schema evolution)  
Implement medallion architecture (Bronze-Silver-Gold)  
Data lineage  
Implement an AI/ML model as part of the data pipeline.  
Performance tuning (e.g., partitioning, z-ordering, etc.)   
Basic visualization (plots, dashboard, ...)  
Record and present pipeline statistics (e.g., number of ingested records, ingestion timing)	   
External visualization or other type of data usage via API/sharing protocols  
Simple data contract  
Access the data product through an API  
Automated testing of schema/data  

## 3) Data  
Any reference to time or in this section referes to the epoch seconds at which the sampling began.  
Any sort of positivity is a float within [-1,1].  
Impressions refer to an approximated number. Not an exact value, unless the platform happens to provide such.  

### 3.1) Tables  
  3po.main.timeline: This is the main timeseries, and includes time, and the corresponding {platform}_positivity for each platform.  
  3po.main.{platform}_positivity, for each platform: Include ID and positivity for each post that has been sampled from that platform.  
  3po.main.ingests: Includes the time, instances of posts sampled, how many of these posts were new, and thus required more processing, and how many files were saved to represent those posts.  
  3po.h{platform}.h{ID}, for each post: H is short for history. Includes every timestamp at which an instance of the post was sampled, and the number of impressions at that time.  
  3po.t{platform}.t{time}, for each platform and sample: T is short for timestamp. Includes the ID, impressions, and positivity of each post sampled from that platform at that time.  

### 3.2) Volumes  
  3po.main.timeline: containst yaml files called: timeline, positivity, ingests, history, and timestamp, each of which provides the data contract for the corresponding tables.  
  3po.c{platform}.{ID} for each post: C is short for content. Includes the content of each post. Text content is stored as 0.txt. Additional files are numerically named with various file formats.  
  3po.responses.{platform} for each platform: contains json files named after time. These represent the original response from which data is gathered.  

## 4) Code files & user guide

### 4.1) Notebooks  
Setup: Prepares the locations and files that aren't time or platform specific. To use, simply run all cells in order.
  
Ingestion: Responsible for collecting, transforming, and storing data. Cells four and five handle specific platforms. If another platform is to be added, a new cell needs to be added following the same structure. Cell 6 would also require some edits to accomodate more plattforms. The locations that need change are commented and intuitive. The last cell is for calling functions. Sample(time,limit) is used to take a sample. Time determines the epoch second the sample will be listed under, and limit determines the number of posts sampled from each platform. Ingest(samples,size,period) runs the sample() function a number of times equal to samples. time is set to the current time, and limit is equivalent to size. Period determines the lenght of time between samples starting. If a sample would start before the previous one has ended, it will instead start imediately after. If samples is negative, the sampling will continue unless interrupted.

Reset: The first cell defines functions for clearing certain data. The second cell is for calling those functions. Especially usefull if dealing with low storage quotas.

API_Helper: Potentially usefull when setting up the API. First cell provides permissions. Second cell provides the workspace URL. To use, edit the Service Principal ID.

Query: Provides a space to query tables for debugging.

### 4.2) API  
The API is implemented through a Databricks App. To use it, create and deploy an app using the API folder, connect a service principal, and edit and run the API_Helper notebook.
The API provides an endpoint for each table. These are automatically tested using the contracts. These endpoints are:
/timeline, /ingests, /timestamp/{platform}/{time}, /history/{platform}/{id}, and /positivity/{platform}.
It also provides /positivity/{platform}/{id}, which simply returns the positivity of the post; /content/{platform}/{id}, which returns a file or folder containing the content of the post; and /response/{platform}/{time} which returns the original response of the platform at the time.

### 4.3) Visualizer  
The visualizer is also a notebook, however, it is meant to run outside of Databricks to visualize data it recieves through API calls. The first cell includes all imports. Note that running it might require installs first. Installs are not included in the notebook. The second cell defines query variables. These can be edited to visualize different sets of data. The third cell generates access to the API. The four first rows define variables that should be eddited to match the app and its service principal. It also requires a secret for the service principal, which may be generated in settings inside Databricks. The fourth cell defines the calls and visualizations. Subsequent cells can be run to call and visualize data.

## 5) Pipeline  
First, a call is made to the plattform, which provides information about the most popular post. This is saved as 3po.main.responses.{platform}.{time} For each post in the response, the ID is compared against
3po.main.{platform}_positivity. If the ID is present in the table, this is an instance of a previously handeled post. If so, only the values needed to calculate impressions are collected from the platform, and the positivity is collected from the file. Rows are then appended to the timestamp and history of the post. If there is no ID match, it is a new post, and the positivity is calculated by using Vader sentiment analysis on the user facing text elements of the post. Also, the contents of the post are downloaded and stored in 3po.c{platform}.{ID}. Appends are then performed as if the post was reoccuring.

Once this is done for each post in the response. The average positivity weighted by impressions is calculated. Posts with no text elements are ignored. When this has been done for all platforms, rows are appended to timeline and ingests. From there, the data is accessible through the API, which also performs automatic testing if the data is a table.

## 6) Details of task implementation  

'Description of solution with illustrative elements. Data schema description and pipeline description.'  
This file is in large part an implementation of this task.

'Repository organization & documentation', 'Overall presentation & language', 'Scope & innovativeness, originality'  
These tasks are impossible not to implement, although the quality of implementation can vary.

'Structured data (batch/manual)', 'Unstructured data (batch/manual)', 'Real-time or automated batch ingestion'  
The responses are structured, if not to the standards of a table. If a platform was to send a table, the system could also handle it. The different files are definitely unstructured.
Sample() is an example of batch ingestion, and ingest() is thus an example of automated batch ingestion.

'Implement ETL to clean, transform, and standardize data', 'Implement an AI/ML model as part of the data pipeline.'  
Various variables are reconciled into impressions. AI is implemented in the form os sentiment analysis.

'Apply data deduplication & type validation, basic metadata', 'Advanced/automated metadata (e.g., profiling, schema evolution)', 'Implement medallion architecture (Bronze-Silver-Gold)', 'Data lineage', 'Performance tuning (e.g., partitioning, z-ordering, etc.)'  
Deduplication was most cruscially implemented by not treating each instance of a post as a new post, which among other things would require new file downloads. Data lineage and partitioning are both implemented by categorizing data primarily by plattoform and secondarily by time. The bronze layer consists of content and responses. The silver layer includes timestamps and history. The timeline is the gold layer the pipeline builds towards. Everything else is there to calculate or verify it, or to provide system information.

'Basic visualization (plots, dashboard, ...)', 'Record and present pipeline statistics (e.g., number of ingested records, ingestion timing)', 'External visualization or other type of data usage via API/sharing protocols', 'Simple data contract', 'Access the data product through an API', 'Automated testing of schema/data'  
The data can be accessed through an API, which includes automated testing with data contracts. This API is called by an external visualizer that can draw plots, of various data, including pipeline statistics.

## 7) Disclosure of AI usage  
Each function has gone through several iterations, and nearly all of them have at some point been edited by, or had parts of them generated by Claude Sonnet 4.6, a large language model. In some cases, Claude generated early drafts, in other cases it was used for the final changes. That being said, the model has not, and could not have been used to produce the final iterations from scratch or without intervention.
While the model was a significant contributor to coding, I retain complete, direct authorship of the system at the top and middling layers. In other words, the AI was allowed to execute my ideas, but not to fill in any blanks. Any response that fell outside of this restriction resulted in either a more specificed prompt, or me doing the task manually. The built in assistant was also used occasionally, but rarely to any benefit.

Various large language models were consulted early on to find working plattforms. While the error rates were high, the plattforms that were ultimately chosen were sugested by several models. Various models, but mostly Claude, were also used to navigate Databricks early on, and again during the creation of the API.

Lastly, for completion, it can be reiterated that the positivity of a post is determined by Vader sentiment analysis, which is also a form of AI. This however, is only part of the pipeline, not a contributor to its creation.
