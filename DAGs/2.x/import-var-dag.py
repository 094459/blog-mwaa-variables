from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

# to use this, create a file with your variables and deploy it to your DAGS folder
# the invoke this DAG using a conf file
# { "var_filename" : "name of the variable file you copied to the DAGS folder"}
# e.g { "var_filename" : "variables.json" }

with DAG(
    dag_id="import_airflow_variables",
    schedule_interval=None,
    catchup=False,
    start_date=days_ago(1)) as dag:

    get_var_filename = BashOperator(
        task_id="get_var_filename",
        bash_command='echo "You are importing the following variable file: \'{{ dag_run.conf["var_filename"] if dag_run.conf else "No filename supplied" }}\'"',
    )
    task1 = BashOperator(
        task_id="create_variables",
        bash_command='airflow variables import /usr/local/airflow/dags/{{ dag_run.conf["var_filename"] if dag_run.conf else "variables.json"}}'
   )
   