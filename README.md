# 3PO
Parallel Post Positivity Observer

1) Introduction  
The top level prouct of this pipeline is a timeseries of 'positivity' across multiple platforms; by running sentiment analysis
on the most popular posts, and weighting them based on approximation of impressions. The system also stores several other tables and files, 
that were part of the pipeline, or otherwise provide more clarity about the posts or the system. These will be listed in section 3.
The code is currently set up to track the social media platforms Bluesky and Mastodon, but the system is made to be expandable, only
requireing changes in the Ingestion notebook [link]. Early versions tracked Redit as well, but the endpoint was not open to Databricks.

2) Completed tasks  
In short, this project includes all tasks with the exception of 'Structured logging & error handling'. As per the instructions, completed tasks
will be listed here. How these were implemented will be described batchwise in section 5, by which the structure of the project should be clearer.  
  Description of solution with illustrative elements. Data schema description and pipeline description.  
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

3) Data  
Any reference to time or timestamp in this section referes to the epoch seconds at which the sampling began.  
Any sort of positivity is a float within [-1,1].  
Impressions refer to an approximated number. Not an exact value, unless the platform happens to provide such.  

3.1) Tables:  
  3po.main.timeline: This is the main timeseries, and includes time, and the corresponding {platform}_positivity for each platform.  
  3po.main.{platform}_positivity, for each platform: Include ID and positivity for each post that has been sampled from that platform.  
  3po.main.ingests: Includes the time, instances of posts sampled, how many of these posts were new, and thus required more processing, and how many files were saved to represent those posts.  
  3po.h{platform}.h{ID}, for each post: includes every timestamp at which an instance of the post was sampled, and the number of impressions at that time.  
  3po.t{platform}.t{time}, for each platform and sample: includes the ID, impressions, and positivity of each post sampled from that platform at that time.  

3.2) Volumes:  
  3po.main.timeline: containst yaml files called: timeline, positivity, ingests, history, and timestamp, each of which provides the data contract for one row of section 3.1, listed in corresponding order.  
  3po.c{platform}.{ID} for each post: includes the content of each post. Text content is stored as 0.txt. Additional files are numerically named with various file formats.  
  3po.responses.{platform} for each platform: contains json files named after time. These represent the original response from which data is gathered.  
