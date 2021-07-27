from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable

demo = "{variable_placeholder}"

with DAG(
    dag_id="display_changed_variables",
    schedule_interval=None,
    catchup=False,
    start_date=days_ago(1)) as dag:

    get_var_filename = BashOperator(
        task_id="disp_variable",
        bash_command='echo "The value of the variable is: {var}"'.format(var=demo),
    )
   