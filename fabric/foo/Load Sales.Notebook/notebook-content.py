# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "a1000000-0000-4000-8000-000000000001",
# META       "default_lakehouse_name": "Sales",
# META       "default_lakehouse_workspace_id": "00000000-0000-0000-0000-000000000000",
# META       "known_lakehouses": [
# META         {
# META           "id": "a1000000-0000-4000-8000-000000000001"
# META         }
# META       ]
# META     }
# META   }
# META }

# MARKDOWN ********************

# # Load Sales
#
# Writes a small `sales` table into the default lakehouse so the semantic model
# has something to read. Deterministic, so a re-run is a no-op in effect.

# CELL ********************

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
