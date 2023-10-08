import biobricks as bb
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("pubmed").getOrCreate()
df = spark.read.parquet(bb.assets("pubmed")[0])
df.limit(10).show()