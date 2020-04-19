from django.db import models
from django.core.validators import MaxValueValidator,MinValueValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Create your models here.
class Indicador(models.Model):
    FINANCIERO = 1
    CLIENTE = 2
    PROCESOS_INTERNOS = 3
    APRENDIZAJE_Y_CRECIMIENTO = 4
    CATEGORIAS = (
        (FINANCIERO, 'Financieros'),
        (CLIENTE, 'Clientes'),
        (PROCESOS_INTERNOS, 'Procesos Internos'),
        (APRENDIZAJE_Y_CRECIMIENTO, 'Aprendizaje y Crecimiento'),
    )
    nombre_kpi = models.CharField(max_length=30, unique=True)
    meta_kpi = models.PositiveIntegerField(validators=[
            MaxValueValidator(90000),
            MinValueValidator(1)
        ])
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    categoria = models.PositiveSmallIntegerField(choices=CATEGORIAS)
    descripcion_kpi = models.CharField(null = True, blank= True, max_length=100)
    unidad_medida = models.CharField(max_length=15, blank=False, null=False)
    responsable = models.ForeignKey(User, on_delete=models.CASCADE, blank= True, null=True)
   

    def __str__(self):
        return self.nombre_kpi


class Info_kpi(models.Model):
    valor_kpi = models.PositiveIntegerField(default=0)
    fecha_modificacion = models.DateTimeField(auto_now_add=True)
    observacion = models.CharField(null = True, blank= True, max_length=100)
    indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.indicador)

class Acumulado_kpi(models.Model):
    fecha = models.DateField(auto_now_add=True)
    acumulado = models.IntegerField(null = True, blank= True,
    validators=[
            MaxValueValidator(5000),
            MinValueValidator(0)
        ])
    meta_mensual = models.PositiveIntegerField(default=0,null = True, blank= True)
    porcentaje = models.DecimalField(null = True, blank= True, max_digits=100, decimal_places=2)
    proyeccion = models.DecimalField(null = True, blank= True, max_digits=100, decimal_places=2)
    indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.indicador)


class Incidentes(models.Model):
    titulo_incidente= models.CharField(max_length=40, unique=True)
    fecha_incidente = models.DateTimeField(auto_now_add=True)
    causa_incidente = models.CharField(null = True, blank= True, max_length=100)
    indicadores_afectados = models.ManyToManyField(Indicador)
    registrador = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo_incidente

class Compromisos(models.Model):
    COMPLETADA = 1
    EN_PROCESO = 2
    PENDIENTE = 3
    ESTATUS = (
        (COMPLETADA, 'Completada'),
        (EN_PROCESO, 'En Proceso'),
        (PENDIENTE, 'Pendiente'),
        
    )
    correcion_incidente = models.CharField(max_length=100)
    fecha_plazo = models.DateField()
    estado_compromiso = models.SmallIntegerField(choices=ESTATUS)
    responsable = models.ForeignKey(User, on_delete=models.CASCADE)
    id_incidente = models.ForeignKey(Incidentes, on_delete=models.CASCADE)


class Reunion(models.Model):
    fecha_reunion = models.DateField(unique=True)
    participantes = models.ManyToManyField(User)

    def __str__(self):
        return str(self.fecha_reunion)