import pandas as pd
def generate_kpis(
    employee_df,
    task_df
):

    total_employees = len(employee_df)

    total_tasks = len(task_df)

    completed_tasks = len(
        task_df[
            task_df["status"] == "Completed"
        ]
    )

    completion_rate = round(
        (
            completed_tasks / total_tasks
        ) * 100,
        2
    ) if total_tasks else 0

    return {
        "employees": total_employees,
        "tasks": total_tasks,
        "completed": completed_tasks,
        "completion_rate": completion_rate,
    }


def team_performance_summary(
    employee_df,
    task_df
):

    merged = task_df.merge(
        employee_df,
        left_on="employee_id",
        right_on="id",
        suffixes=(
            "_task",
            "_employee"
        )
    )

    summary = merged.groupby(
        "department"
    ).agg({
        "id_task": "count",
        "hours": "sum"
    }).reset_index()

    summary.columns = [
        "Department",
        "Total Tasks",
        "Total Hours"
    ]

    return summary