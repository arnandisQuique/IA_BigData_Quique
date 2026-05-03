from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, avg, stddev, last
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

# 1. ESQUEMA DE LOS DATOS (Debe coincidir con el JSON de Binance @miniTicker)
# 's': symbol, 'c': close price, 'E': event time
schema = StructType([
    StructField("s", StringType(), True),
    StructField("c", StringType(), True),
    StructField("E", DoubleType(), True) # Timestamp en milisegundos
])

# 2. INICIALIZAR SESIÓN DE SPARK
spark = SparkSession.builder \
    .appName("CryptoStreamingProcessor") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoints") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 3. LECTURA DE KAFKA
# 'kafka:9092' es el nombre del servicio en docker-compose
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "crypto_raw_data") \
    .option("startingOffsets", "latest") \
    .load()

# Convertir el binario de Kafka a JSON y aplicar esquema
json_df = raw_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# 4. PRE-PROCESAMIENTO
# Convertimos el precio a Double y el EventTime a Timestamp
processed_df = json_df.withColumn("precio", col("c").cast(DoubleType())) \
    .withColumn("timestamp", (col("E") / 1000).cast(TimestampType())) \
    .withColumn("par", col("s"))

# 5. CÁLCULO DE INDICADORES (Ventanas Temporales)
# Ejemplo: Media Móvil de los últimos 5 minutos, recalculada cada 30 segundos
windowed_stats = processed_df \
    .withWatermark("timestamp", "1 minute") \
    .groupBy(
        window(col("timestamp"), "5 minutes", "30 seconds"),
        col("par")
    ) \
    .agg(
        avg("precio").alias("media_movil"),
        last("precio").alias("precio_actual"),
        stddev("precio").alias("volatilidad")
    )

# 6. ESCRITURA EN HDFS (Formato Parquet Particionado)
# Esta parte guarda el histórico para luego consultarlo con Hive
query_hdfs = processed_df \
    .writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("path", "hdfs://namenode:9000/data/cripto/") \
    .partitionBy("par") \
    .start()

# 7. SALIDA A CONSOLA (Para debug inicial)
query_console = windowed_stats \
    .writeStream \
    .outputMode("update") \
    .format("console") \
    .start()

query_hdfs.awaitTermination()
query_console.awaitTermination()