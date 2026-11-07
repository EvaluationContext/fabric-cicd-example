# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "a77c7000-9e05-47f1-85a5-4db985d45676",
# META       "default_lakehouse_name": "Sales",
# META       "default_lakehouse_workspace_id": "5cc9c02d-5413-4ef5-857f-e8111338c908",
# META       "known_lakehouses": [
# META         {
# META           "id": "a77c7000-9e05-47f1-85a5-4db985d45676"
# META         }
# META       ]
# META     }
# META   }
# META }

# MARKDOWN ********************

# # Load Sales
# # Writes a small `sales` table into the default lakehouse so the semantic model
# has something to read. Deterministic, so a re-run is a no-op in effect.

# CELL ********************

# a change from feature

from pyspark.sql import Row

rows = [
    Row(order_id=1, region="North", amount=120.50),
    Row(order_id=2, region="South", amount=80.00),
    Row(order_id=3, region="East", amount=200.25),
    Row(order_id=4, region="West", amount=55.75),
]

df = spark.createDataFrame(rows)
df.write.mode("overwrite").format("delta").saveAsTable("sales")
display(spark.sql("SELECT region, SUM(amount) AS amount FROM sales GROUP BY region"))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
