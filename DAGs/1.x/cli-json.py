from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
with DAG(dag_id="cli-json", schedule_interval=None, catchup=False, start_date=days_ago(1)) as dag:
    env_output_json = BashOperator(
        task_id="list_dir",
        bash_command='ls /usr/local/airflow/ && ls /usr/local/airflow/dags/'
    )
    env_output_json = BashOperator(
        task_id="cli_output_json",
        bash_command='echo "1)Here is the message: \'{{ dag_run.conf["cli_test"] if dag_run else "" }}\'"',
    )
    env_output_json = BashOperator(
        task_id="cli_output2_json",
        bash_command='echo "2)Here is the message: \'{{ dag_run.conf["cli_test2"] if dag_run else "" }}\'"',
    )    
    env_output_json = BashOperator(
        task_id="cli_output3_json",
        bash_command='echo "3)Here is the message: \'{{ dag_run.conf["cli_test3"] if dag_run else "" }}\'"',
    )