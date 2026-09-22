import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# Converts numeric month to its full name string representation
def month_name(month: int):
    return {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }[month]

# Safely reads and parses a JSON file, returning None if there's an error
def read_json_file(file_path):
    try:
        with open(file_path, 'r') as f: 
            return json.load(f)
    except (json.JSONDecodeError, IOError):
       # Skip or flag invalid or unreadable files silently 
        return None 

# Processes all JSON files in a month folder and returns their data as a list
def process_month_folder(month_path, month):
    data = []
    for file in os.listdir(month_path):
        if file.endswith('.json'):
            file_data = read_json_file(os.path.join(month_path, file))
            if file_data:
                data.append(file_data)
    return data

# Reads and organizes JSON files from a hierarchical year/month directory structure
def read_json_files_by_year_month(root_directory):
    data_by_year_month = {}
    
    for year_folder in os.listdir(root_directory):
        year_path = os.path.join(root_directory, year_folder)
        if not (os.path.isdir(year_path) and year_folder.isdigit()):
            continue
            
        year = int(year_folder)
        data_by_year_month[year] = {}
        
        for month_folder in os.listdir(year_path):
            month_path = os.path.join(year_path, month_folder)
            if not (os.path.isdir(month_path) and month_folder.isdigit()):
                continue
                
            month = int(month_folder)
            month_key = month_name(month)
            data_by_year_month[year][month_key] = process_month_folder(month_path, month)
    
    return data_by_year_month

# Calculates monthly statistics including record counts and follow-up visits
def calculate_monthly_stats(months):
    monthly_counts = []
    for month, records in months.items():
        # Count total follow-up visits where follow_up_needed is True
        follow_up_visits = sum(1 for record in records if record['follow_up_needed'])
        monthly_counts.append({
            "month": month,
            "record_count": len(records),
            "follow_up_visits": follow_up_visits
        })
    return monthly_counts

# Processes department-specific data to extract diagnosis, treatment, and duration statistics
def process_department_data(department_name, department_df):
    # Get top 2 most common diagnoses with their frequencies
    common_diagnosis = department_df['diagnosis'].value_counts().head(2)
    common_diagnosis = [{"diagnosis": k, "frequency": v} for k, v in common_diagnosis.items()]
    
    # Get top 2 most common treatments with their frequencies
    common_treatment = department_df['treatment'].value_counts().head(2)
    common_treatment = [{"treatment": k, "frequency": v} for k, v in common_treatment.items()]
    
    # Calculate average treatment duration, defaulting to 0 if no data
    avg_duration = department_df['treatment_duration'].mean() if not department_df['treatment_duration'].empty else 0
    
    return {
        "department_name": department_name,
        "total_visits": len(department_df),
        "common_diagnosis": common_diagnosis,
        "common_treatment": common_treatment,
        "avg_treatment_duration": round(avg_duration.item(), 2)
    }

# Aggregates medical records data into yearly statistics with department breakdowns
def aggregate_data(data):
    aggregated_stats = {}
    
    for year, months in data.items():
        # Combine all records for the year into a single DataFrame
        all_records = []
        for records in months.values():
            all_records.extend(records)
            
        df = pd.DataFrame(all_records)
        total_records = len(df)
        
        monthly_counts = calculate_monthly_stats(months)
        outcome_distribution = df['outcome'].value_counts().to_dict()
        
        # Process data for each department separately
        department_data = [
            process_department_data(department, department_df)
            for department, department_df in df.groupby('department')
        ]
        
        aggregated_stats[year] = {
            "year": year,
            "total_records": total_records,
            "departments": department_data,
            "monthly_summary": monthly_counts,
            "overall_outcomes": outcome_distribution
        }
    
    return aggregated_stats

# Writes department statistics and highlights to the report file
def write_department_highlights(f, departments):
    f.write("Department Highlights\n")
    f.write("-------------------\n")
    for dept in departments:
        f.write(f"The {dept['department_name']} Department handled {dept['total_visits']} patient visits this year.\n")
        
        if dept['common_diagnosis']:
            # Format diagnosis statistics into a readable string
            diagnoses = [f"{d['diagnosis']} ({d['frequency']} cases)" for d in dept['common_diagnosis']]
            if len(diagnoses) > 1:
                f.write(f"The most frequently addressed conditions were {', '.join(diagnoses[:-1])} and {diagnoses[-1]}.\n")
            else:
                f.write(f"The most common condition treated was {diagnoses[0]}.\n")
        
        f.write(f"Patients in this department typically underwent treatment for an average of ")
        f.write(f"{dept['avg_treatment_duration']} days.\n\n")

# Writes the annual overview section of the report
def write_year_overview(f, stats, busiest_month, total_followups, year):
    f.write(f"Medical Center Annual Review {year}\n")
    f.write("=" * 50 + "\n\n")
    
    f.write("Year in Review\n")
    f.write("--------------\n")
    f.write(f"In {year}, our medical center served a total of {stats['total_records']} patients,\n")
    f.write(f"demonstrating our continued commitment to community health. {busiest_month['month']} emerged as\n")
    f.write(f"our busiest period with {busiest_month['record_count']} patient visits. Our dedication to comprehensive\n")
    f.write(f"care is reflected in the {total_followups} follow-up appointments conducted throughout the year,\n")
    f.write("ensuring optimal recovery and treatment outcomes for our patients.\n\n")

# Writes treatment outcome statistics to the report
def write_outcomes(f, outcomes, total_records):
    f.write("Patient Outcomes\n")
    f.write("---------------\n")
    # Calculate and format percentage for each outcome
    outcome_text = []
    for outcome, count in outcomes.items():
        percentage = (count / total_records) * 100
        outcome_text.append(f"{outcome}: {count} patients ({percentage:.1f}%)")
    f.write(", ".join(outcome_text))

# Generates a comprehensive text summary of the year's medical data
def generate_summary(data):
    for year, stats in data.items():
        file_name = f"{year}_summary.txt"
        departments = stats['departments']
        monthly_data = stats['monthly_summary']
        outcomes = stats['overall_outcomes']
        
        # Find the month with highest patient visits
        busiest_month = max(monthly_data, key=lambda x: x['record_count'])
        total_followups = sum(month['follow_up_visits'] for month in monthly_data)
        
        with open(file_name, 'w') as f:
            write_year_overview(f, stats, busiest_month, total_followups, year)
            write_department_highlights(f, departments)
            write_outcomes(f, outcomes, stats['total_records'])

# Saves annual statistics to JSON files for future reference
def annual_report(data):
    for year, stats in data.items():
        file_name = f"{year}_annual_report.json"
        with open(file_name, 'w') as f:
            json.dump(stats, f, indent=2)

# Creates visualizations of key medical center statistics
def create_visualizations(data):
    for year, stats in data.items():
        plt.rcParams['figure.facecolor'] = 'white'
        fig = plt.figure(figsize=(15, 10))
        gs = GridSpec(2, 2, figure=fig)
        
        # Monthly Visits Bar Chart
        ax1 = fig.add_subplot(gs[0, 0])
        monthly_data = pd.DataFrame(stats['monthly_summary'])
        bars = ax1.bar(monthly_data['month'], monthly_data['record_count'], color='#2ecc71')
        ax1.set_title('Monthly Patient Visits', y=1.05)
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Number of Visits')
        ax1.grid(axis='y', linestyle='--', alpha=0.7)
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}', ha='center', va='bottom')
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Department Distribution Pie Chart
        ax2 = fig.add_subplot(gs[0, 1])
        departments = pd.DataFrame(stats['departments'])
        colors = ['#3498db', '#e74c3c', '#f1c40f', '#9b59b6', '#1abc9c']  
        wedges, texts, autotexts = ax2.pie(departments['total_visits'], 
                                          labels=departments['department_name'], 
                                          autopct='%1.1f%%',
                                          colors=colors,
                                          explode=[0.05]*len(departments))
        ax2.set_title('Patient Distribution by Department', y=1.05)
        plt.setp(autotexts, size=8, weight="bold")
        plt.setp(texts, size=8)

        # Treatment Outcomes Bar Chart
        ax3 = fig.add_subplot(gs[1, 0])
        outcomes = pd.Series(stats['overall_outcomes'])
        bars = ax3.bar(outcomes.index, outcomes.values, color='#3498db')
        ax3.set_title('Treatment Outcomes', y=1.05)
        ax3.set_xlabel('Outcome')
        ax3.set_ylabel('Number of Patients')
        ax3.grid(axis='y', linestyle='--', alpha=0.7)
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}', ha='center', va='bottom')
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Average Treatment Duration by Department
        ax4 = fig.add_subplot(gs[1, 1])
        bars = ax4.bar(departments['department_name'], departments['avg_treatment_duration'], color='#e74c3c')
        ax4.set_title('Average Treatment Duration by Department', y=1.05)
        ax4.set_xlabel('Department')
        ax4.set_ylabel('Days')
        ax4.grid(axis='y', linestyle='--', alpha=0.7)
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom')
        plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')

        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
        plt.savefig(f'{year}_analytics.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
# Predefined root directory
root_directory = "data" 

# Check if the directory exists
if not os.path.isdir(root_directory):
    # Exit naturally by not proceeding further 
    exit()
    
# Proceed with the script if the directory is valid
records = read_json_files_by_year_month(root_directory)
aggregated_stats = aggregate_data(records)

annual_report(aggregated_stats)
generate_summary(aggregated_stats)
create_visualizations(aggregated_stats)