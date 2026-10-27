-- Reto 3: escribe aquí tu consulta de la Misión 3.
-- Hay una consulta de referencia en sql/consulta_dataset.sql.
-- Revisa el LEFT JOIN, la agrupación y los nombres de las seis columnas.

SELECT
  c.id_cliente,
  c.antiguedad_meses,
  COUNT(o.id_operacion) AS num_operaciones,
  IFNULL(SUM(o.importe),0) AS gasto_total,
  IFNULL(ROUND(AVG(o.importe),2),0) AS ticket_medio,
  c.abandono
FROM clientes c
LEFT JOIN operaciones o
  ON c.id_cliente = o.id_cliente
GROUP BY
  c.id_cliente,
  c.antiguedad_meses,
  c.abandono;
