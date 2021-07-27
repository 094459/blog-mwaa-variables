from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

with DAG(
    dag_id="airflow_variables_atruntime",
    schedule_interval=None,
    catchup=False,
    start_date=days_ago(1)) as dag:

    get_var_filename = BashOperator(
        task_id="get_var_filename",
        bash_command="""echo 'You are running this DAG with the following variable file: "{{ dag_run.conf["cli_test"] if dag_run.conf else var.value.cli_test }}"'""",
    )
    get_var_filename = BashOperator(
        task_id="get_var_filename2",
        bash_command='echo "You are running this DAG with the following variable file: \'{{ dag_run.conf["cli_test2"] if dag_run.conf else var.value.cli_test2 }}\'"',
    )
    get_var_filename = BashOperator(
        task_id="get_var_filename3",
        bash_command='echo "You are running this DAG with the following variable file: \'{{ dag_run.conf["cli_test3"] if dag_run.conf else var.value.cli_test3 }}\'"',
    )
#var.value.cli_test
