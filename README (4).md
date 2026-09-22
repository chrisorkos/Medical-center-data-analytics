# Medical Center Data Analytics

This script processes medical center data to generate annual reports, summaries and visualisations. It provides analysis into patient visits, department activities, treatment outcomes and follow up appointments, providing meaningful statistics and notable trends.

Requirements
------------

1. Python Environment:
   - Python 3.x
   - Required Package: pandas, matplotlib

2. Input Data Structure:
   Root Directory
      ── Year Folders (e.g., "2022", "2023")
         ── Month Folders (1-12)
            ── JSON files containing patient records

   Each JSON file should at least contain:
   - diagnosis
   - treatment
   - treatment_duration
   - follow_up_needed
   - department
   - outcome

How to Run
----------

1. Create virtual environment (if not already created):

   Windows:
   - python -m venv .venv
   - .venv\Scripts\activate
   - pip install pandas matplotlib

2. Run the script:

   python medical_center_data_analytics.py

Output Files
------------

The script generates three types of files for each processed year:

1. YYYY_annual_report.json
   Description: Contains aggregated statistics for the year, including:

   - Total patient visits
   - Monthly visit summaries
   - Department specific statistics (common diagnoses, treatments, average treatment duration)
   - Overall treatment outcomes

2. YYYY_summary.txt
   Description: A text summary highlighting:

   - Notable trends
   - Busiest periods
   - Follow up appointments
   - Department highlights
   - Patient outcomes

3. YYYY_analytics.png (Visualisation)
   Description: Graphical representations of the following:

   - Monthly patient visits
   - Patient distribution by department
   - Treatment outcomes
   - Average treatment duration by department

Note: Ensure your data directory structure matches the required format for proper processing.

Visualisations
--------------

This script generates visual summaries for each year, saved as PNG files:

1. Monthly Patient Visits (Bar Chart):
   Displays the number of patient visits for each month in the year.

2. Department Distribution (Pie Chart):
   Percentage of visits handled by each department

3. Treatment Outcomes (Bar Chart):
   Summarises the outcomes of treatments

4. Average Treatment Duration by Department (Bar Chart):
   Compares the average number of days patients undergo treatment in each department.

Error Handling
--------------

The script handles errors gracefully by:

- Skipping or flagging invalid or unreadable JSON files without causing an error in the script.
- If the root directory is missing or incorrect, the script stops execution.
