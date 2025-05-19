FROM apache/kafka:3.7.0

# Copy the JMX exporter agent and config
COPY jmx_prometheus_javaagent-1.2.0.jar /opt/
COPY kafka.yml /opt/

# Expose the JMX Exporter port
EXPOSE 7071

# Set the JMX options
ENV KAFKA_OPTS="-javaagent:/opt/jmx_prometheus_javaagent-1.2.0.jar=7071:/opt/kafka.yml"

# Kafka startup already uses these envs:
# You don’t need to override ENTRYPOINT or CMD unless custom logic is needed