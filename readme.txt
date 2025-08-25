Para que la función fitness funcione debe de existir un archivo llamado type-chart.json con la información de la tabla de tipos.

En el archivo genetico_explicado_sinPareto, se encuentra la idea inicial de la memoria de hacerlo todo en la mismo archivo, memoria y código, cosa que resultó poco práctica a posteriori.

genetico_sinPareto y enfriamiento_sinPareto dependen de fitness.py

En cambio genetico_conPareto, no depende de fitness.py porque no resultaba práctico tenerlo en un archivo separado para hacer los precalculos.

También es posible que a la hora de hacer el precalculo de las estadisticas individuales se obtenga un error de conexión con base de datos por hacer demasiadas peticiones simultaneas. Para arreglarlo agrega antes de cada petición o ejecuta el método de continuar calculando del archivo genetico_sinPareto

