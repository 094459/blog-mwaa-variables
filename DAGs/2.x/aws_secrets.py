from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable

demo =  Variable.get("cli_test", default_var="undefined")

with DAG(
    dag_id="aws_secrets_variables",
    schedule_interval=None,
    catchup=False,
    start_date=days_ago(1)) as dag:

    get_var_sec1 = BashOperator(
        task_id="disp_aws_secret_variable_1",
        bash_command='echo "The value of the variable is: {var}"'.format(var=demo),
    )

    get_var_sec2 = BashOperator(
        task_id="disp_aws_secret_variable_2",
        bash_command='echo "The value of the second variable is: {{var.value.cli_test3}}"',
    )

   