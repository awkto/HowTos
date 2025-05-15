## GitLab CI Conditions

Here are some working examples of conditions in GitLab CI jobs. The uses cases are
- Running a job only on Branch pushes
- Running a job only on Merge Requests
- Running a job only on Merge Results Pipelines
- Running a job only on Merge Trains

**Branch Pipelines**
Variables : 
- $CI_PIPELINE_SOURCE          = `push`
- $CI_MERGE_REQUEST_EVENT      = ` `
- $CI_MERGE_REQUEST_EVENT_TYPE = ` `
- $CI_MERGE_REQUEST_TRAIN_FLAG = ` `


**Merge Request Pipelines**
Variables :
- $CI_PIPELINE_SOURCE          = `merge_request_event`
- $CI_MERGE_REQUEST_EVENT      = ` `
- $CI_MERGE_REQUEST_EVENT_TYPE = `detached`
- $CI_MERGE_REQUEST_TRAIN_FLAG = ` `


**Merge Result Pipelines**
Variables :
- $CI_PIPELINE_SOURCE          = `merge_request_event`
- $CI_MERGE_REQUEST_EVENT      = ` `
- $CI_MERGE_REQUEST_EVENT_TYPE = `merge_result`
- $CI_MERGE_REQUEST_TRAIN_FLAG = ` `


**Merge Train Pipelines**
Variables :
- $CI_PIPELINE_SOURCE          = `merge_request_event`
- $CI_MERGE_REQUEST_EVENT      = ` `
- $CI_MERGE_REQUEST_EVENT_TYPE = `merge_train`
- $CI_MERGE_REQUEST_TRAIN_FLAG = ` `


