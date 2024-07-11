# Overview

## waves.csv Notes
### You must uncomment these two lines in congregate.conf
```
wave_spreadsheet_columns = Wave name, Wave date, Source Url, Parent Path, Override
wave_spreadsheet_column_mapping = {"Wave name": "Wave name", "Wave date": "Wave date", "Source Url":"Source Url", "Parent Path":"Parent Path", "Override":"Override"}
```
 Both lines must match the column names from your waves.csv file (case sensitive)

### Groups are only mapped according to the Projects mapped

Groups without projects must be staged manually without waves

Unstage everything by either blanking out the stage json files OR just stage something else with 
```
congregate stage-groups [id]

 
