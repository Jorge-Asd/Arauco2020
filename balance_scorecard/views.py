from django.shortcuts import render, HttpResponseRedirect, redirect, HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from .forms import IndicadorForm, InformacionForm, AcumuladoForm, InformacionActualizarForm, IncidentesForm, CompromisosForm, ReunionForm
from .models import Indicador, Info_kpi, Acumulado_kpi, User, Incidentes, Compromisos, Reunion
from .forms import IndicadorForm, CustomUserCreationForm, CustomAuthenticationForm
from bootstrap_modal_forms.generic import (BSModalLoginView,
                                           BSModalCreateView,
                                           BSModalUpdateView,
                                           BSModalReadView,
                                           BSModalDeleteView)
from django.contrib.messages.views import SuccessMessageMixin
from bootstrap_modal_forms.mixins import PassRequestMixin
from .forms import CustomUserCreationForm
import datetime
from django.utils.timezone import utc
from django.utils import timezone
from django.db.models import Sum, Count,Max, Avg
from django.views.generic import CreateView, ListView, View
from django.contrib import messages
from django.core.mail import EmailMessage
from jinja2 import Environment, FileSystemLoader
import pdfkit
from balance_scorecard.utils import render_to_pdf
from django.http import JsonResponse

#Librerias charts
from random import randint
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.

class LoginView(BSModalLoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'balance_scorecard/login.html'
    success_message = 'Éxito: ha iniciado sesión correctamente.'
    success_url = reverse_lazy('index')

class RegistroView(BSModalCreateView):
    form_class = CustomUserCreationForm
    template_name = 'balance_scorecard/registro.html'
    success_message = 'Éxito: registro exitoso. Ahora puede iniciar sesión.'
    success_url = reverse_lazy('index')

class ActualizarUsuarioView(generic.UpdateView):
    model = User
    template_name = 'balance_scorecard/perfil.html'
    success_message = 'Éxito: ha actualizado su perfil correctamente.'
    success_url = reverse_lazy('index')


def Index(request):
    model = Indicador
    us = request.user
    indicador = Indicador.objects.filter(responsable__username=us).order_by('id')
    #messages.info(request,'pagina cargada con exito')
    return render(request,'index.html',{'indicador':indicador})


class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        id = Acumulado_kpi.objects.filter(fecha__contains=FechaNow()).order_by('id')
        com = 0
        inc = 0
        for i in Acumulado_kpi.objects.filter(fecha__contains= FechaNow()).order_by('id'):
            if i.acumulado >= i.indicador.meta_kpi:
                com = com+1
            else:
                inc = inc+1
        try:
            completo= round((100*com)/(com+inc),2)
            incompleto= round((100*inc)/(com+inc),2)
            pdf = render_to_pdf('balance_scorecard/reporte_indicadores.html', {'id':id, 'fecha':FechaDia(),'completo':completo,'incompleto':incompleto})
            return HttpResponse(pdf, content_type='application/pdf')
        except:
            pdf = render_to_pdf('balance_scorecard/reporte_indicadores.html', {'id':id, 'fecha':FechaDia()})
            return HttpResponse(pdf, content_type='application/pdf')


class PdfAsistencia(View):
    def get(self, request, *args, **kwargs):
        id = Reunion.objects.filter(fecha_reunion__contains= FechaNow()).order_by('fecha_reunion')
        reunion = Reunion.objects.filter(fecha_reunion__contains= FechaNow()).count()
        usuarios = []
        presente = ''
        for i in Reunion.objects.filter(fecha_reunion__contains= FechaNow()).order_by('fecha_reunion'):
            fecha = i.fecha_reunion
            for p in User.objects.all():
                if i.participantes == p.username:
                    presente = 1+presente
            pdf = render_to_pdf('balance_scorecard/reporte_asistencia.html', {'id':id, 'fecha':fecha,'usuarios':usuarios,'presente':presente})
            return HttpResponse(pdf, content_type='application/pdf')
        pdf = render_to_pdf('balance_scorecard/reporte_asistencia.html', {'id':id})
        return HttpResponse(pdf, content_type='application/pdf')
        

def FechaNow():
    fecha_actual= datetime.datetime.now()
    dia = fecha_actual.strftime("%Y-%m-%d")
    mes_actual = fecha_actual.strftime("%Y-%m")
    return mes_actual

def FechaDia():
    fecha_actual= datetime.datetime.now()
    dia = fecha_actual.strftime("%Y-%m-%d")
    return dia


def BSView(request,pk):
    indicador = Acumulado_kpi.objects.filter(fecha__contains=FechaNow(), indicador__categoria=pk).order_by('id')
    return render(request,'balance_scorecard/balancedscorecard.html',{'indicador':indicador})
    

def Home2(request, pk):
    
    user = request.user
    if user.is_staff and not user.is_superuser:
        fecha_actual= datetime.datetime.now()
        indicador= Info_kpi.objects.filter(fecha_modificacion__contains=FechaNow(), indicador=pk).last()
        acum=Info_kpi.objects.filter(fecha_modificacion__contains=FechaNow(), indicador=pk).aggregate(Sum('valor_kpi'))
        promedio=Info_kpi.objects.filter(fecha_modificacion__contains=FechaNow(), indicador=pk).aggregate(Avg('valor_kpi'))
        pp=promedio.pop('valor_kpi__avg')
        ids=Indicador.objects.get(id=pk)
        objeto_acumulado = Acumulado_kpi.objects.filter(fecha__contains=FechaNow(), indicador=pk).count()
        a=acum.pop('valor_kpi__sum')
        if objeto_acumulado==0 and a is None:
            Acumulado_kpi.objects.create(acumulado=0,indicador=ids)
            return render(request, 'balance_scorecard/home.html',{'indicador':indicador,'a':a})    
        else:
            if objeto_acumulado==0  and a is not None:
                prom_dias = 365/12
                tt = ids.meta_kpi
                f_dias = int(fecha_actual.strftime("%d"))
                proyectado = round(pp*(prom_dias-f_dias),0)
                porcentaje = round((100*a)/tt,2)
                Acumulado_kpi.objects.create(acumulado=a,porcentaje=porcentaje,proyeccion=proyectado,indicador=ids,meta_mensual=tt)
                update= Acumulado_kpi.objects.get(acumulado=a,indicador=ids)
                return render(request,'balance_scorecard/home.html',{'indicador':indicador,'update':update})
        if a is None:
            return render(request, 'balance_scorecard/home.html',{'indicador':indicador,'a':a})
        else:
            update = Acumulado_kpi.objects.get(fecha__contains=FechaNow(), indicador=ids)
            tt = ids.meta_kpi
            f_dias = int(fecha_actual.strftime("%d"))
            prom_dias = 365/12
            proyectado = round(pp*(prom_dias-f_dias),0)
            porcentaje = round((100*a)/tt,2)
            update.acumulado = a
            update.porcentaje = porcentaje
            update.proyeccion = proyectado
            update.meta_mensual = tt
            update.save()
            return render(request, 'balance_scorecard/home.html',{'indicador':indicador,'update':update})

    else:
        if user.is_superuser:
            fecha_actual= datetime.datetime.now()
            indicador= Info_kpi.objects.filter(fecha_modificacion__contains=FechaDia(), indicador=pk)
            acum=Info_kpi.objects.filter(fecha_modificacion__contains=FechaNow(), indicador=pk).aggregate(Sum('valor_kpi'))
            promedio=Info_kpi.objects.filter(fecha_modificacion__contains=FechaNow(), indicador=pk).aggregate(Avg('valor_kpi'))
            pp=promedio.pop('valor_kpi__avg')
            ids=Indicador.objects.get(id=pk)
            objeto_acumulado = Acumulado_kpi.objects.filter(fecha__contains=FechaNow(), indicador=pk).count()
            a=acum.pop('valor_kpi__sum')
            if objeto_acumulado==0 and a is None:
                Acumulado_kpi.objects.create(acumulado=0,indicador=ids)
                return render(request, 'balance_scorecard/home.html',{'indicador':indicador,'a':a})    
            else:
                if objeto_acumulado==0  and a is not None:
                    prom_dias = 365/12
                    tt = ids.meta_kpi
                    f_dias = int(fecha_actual.strftime("%d"))
                    proyectado = round(pp*(prom_dias-f_dias),0)
                    porcentaje = round((100*a)/tt,2)
                    Acumulado_kpi.objects.create(acumulado=a,porcentaje=porcentaje,proyeccion=proyectado,indicador=ids,meta_mensual=tt)
                    update = Acumulado_kpi.objects.get(acumulado=a,indicador=ids)
                    return render(request, 'balance_scorecard/home.html',{'indicador':indicador,'update':update})
            if a is None:
                return render(request, 'balance_scorecard/home.html',{'indicador':indicador},{'a':a})
            else:
                update = Acumulado_kpi.objects.get(fecha__contains=FechaNow(), indicador=ids)
                tt = ids.meta_kpi
                f_dias = int(fecha_actual.strftime("%d"))
                prom_dias = 365/12
                proyectado = round(pp*(prom_dias-f_dias),0)
                porcentaje = round((100*a)/tt,2)
                update.acumulado = a
                update.porcentaje = porcentaje
                update.proyeccion = proyectado
                update.meta_mensual = tt
                update.save()
                return render(request, 'balance_scorecard/home.html',{'indicador':indicador,'update':update})
        else:
            if user.is_authenticated and not user.is_staff and not user.is_superuser:
                fecha_actual= datetime.datetime.now()
                indicador= Info_kpi.objects.filter(fecha_modificacion__contains=FechaDia(), indicador=pk, indicador__responsable__username=user)
                acum=Info_kpi.objects.filter(fecha_modificacion__contains=FechaNow(), indicador=pk).aggregate(Sum('valor_kpi'))
                promedio=Info_kpi.objects.filter(fecha_modificacion__contains=FechaNow(), indicador=pk).aggregate(Avg('valor_kpi'))
                pp=promedio.pop('valor_kpi__avg')
                ids=Indicador.objects.get(id=pk)
                objeto_acumulado = Acumulado_kpi.objects.filter(fecha__contains=FechaNow(), indicador=pk).count()
                a=acum.pop('valor_kpi__sum')
                if objeto_acumulado==0 and a is None:
                    Acumulado_kpi.objects.create(acumulado=0,indicador=ids)
                    return render(request, 'balance_scorecard/home.html',{'indicador':indicador,'a':a})    
                else:
                    if objeto_acumulado==0  and a is not None:
                        prom_dias = 365/12
                        tt = ids.meta_kpi
                        f_dias = int(fecha_actual.strftime("%d"))
                        proyectado = round(pp*(prom_dias-f_dias),0)
                        porcentaje = round((100*a)/tt,2)
                        Acumulado_kpi.objects.create(acumulado=a,porcentaje=porcentaje,proyeccion=proyectado,indicador=ids,meta_mensual=tt)
                        update = Acumulado_kpi.objects.get(acumulado=a,indicador=ids)
                        return render(request, 'balance_scorecard/home.html',{'indicador':indicador,'update':update})
                if a is None:
                    return render(request, 'balance_scorecard/home.html',{'indicador':indicador},{'a':a})
                else:
                    update = Acumulado_kpi.objects.get(fecha__contains=FechaNow(), indicador=ids)
                    tt = ids.meta_kpi
                    f_dias = int(fecha_actual.strftime("%d"))
                    prom_dias = 365/12
                    proyectado = round(pp*(prom_dias-f_dias),0)
                    porcentaje = round((100*a)/tt,2)
                    update.acumulado = a
                    update.porcentaje = porcentaje
                    update.proyeccion = proyectado
                    update.meta_mensual = tt
                    update.save()
                    return render(request, 'balance_scorecard/home.html',{'indicador':indicador,'update':update})




class IndicadorDetalleView(BSModalReadView):
    model = Indicador
    template_name = 'balance_scorecard/detalle.html'


class IndicadorCrearView(BSModalCreateView):
    template_name = 'balance_scorecard/crear.html'
    form_class = IndicadorForm
    success_message = 'Se ha creado indicador exitosamente.'
    success_url = reverse_lazy('index')
    
    def form_valid(self, form):
        form.instance.responsable = self.request.user
        #Enviar Correo electronico
        #email = EmailMessage('Nuevo Indicador Agredado','Nombre Indicador: '+form.instance.nombre_kpi,to=['math1as.molina.m@gmail.com'])
       # email.send()
        return super().form_valid(form)
    

class IndicadorActualizarView(BSModalUpdateView):
    model = Indicador
    template_name = 'balance_scorecard/actualizar.html'
    form_class = IndicadorForm
    success_message = 'Se ha modificado indicador exitosamente.'
    success_url = reverse_lazy('index')


class IndicadorEliminarView(BSModalDeleteView):
    model = Indicador
    template_name = 'balance_scorecard/eliminar.html'
    success_message = 'Se ha eliminado indicador exitosamente.'
    success_url = reverse_lazy('index')

#Crud informacion Kpi

class IndicadorCrearInfoView(BSModalCreateView, SuccessMessageMixin):
    template_name = 'balance_scorecard/crear_info.html'
    form_class = InformacionForm
    success_message = 'Se ha añadido valor al indicador exitosamente.'
    success_url = reverse_lazy('index')

    def get_success_url(self):
        return reverse_lazy('home', args=[self.kwargs['pk']])

    def form_valid(self, form):
        if form.is_valid():
            pk = Indicador.objects.get(id=self.kwargs['pk'])
            objeto = Info_kpi.objects.filter(fecha_modificacion__contains=FechaDia(), indicador=pk).count()
            if objeto==0:
                form.instance.indicador = pk
                return super().form_valid(form)
            else:
                messages.warning(self.request,'El indicador ya tiene un registro del dia')
                success_url = reverse_lazy('index')
                return HttpResponseRedirect(success_url) 
        else:
            return redirect('index.html')

class IndicadorActualizarInfoView(BSModalUpdateView):
    model = Info_kpi
    template_name = 'balance_scorecard/actualizar_info.html'
    form_class = InformacionActualizarForm
    success_message = 'Se ha modificado la informacion con exito.'
    success_url = reverse_lazy('index')

    def get_success_url(self):
        return reverse_lazy('home', args=[self.request.POST.get('indicador')])

#Registro de incidentes

class IncidentesCrearView(BSModalCreateView):
    form_class = IncidentesForm
    template_name = 'balance_scorecard/registro_incidentes.html'
    success_message = 'Registro Guardado exitosamente'
    success_url = reverse_lazy('lista_incidentes')

    def form_valid(self, form):
        form.instance.registrador = self.request.user
        return super().form_valid(form)

class IncidentesActualizarView(BSModalUpdateView):
    model = Incidentes
    template_name = 'balance_scorecard/actualizar_incidentes.html'
    form_class = IncidentesForm
    success_message = 'Incidente Actualizado Correctamente'
    success_url = reverse_lazy('lista_incidentes')

class IncidenteEliminarView(BSModalDeleteView):
    model = Incidentes
    template_name = 'balance_scorecard/eliminar_incidentes.html'
    success_message = 'Se ha eliminado el incidente exitosamente.'
    success_url = reverse_lazy('index')

class IncidenteDetalleView(BSModalDeleteView):
    model = Incidentes
    template_name = 'balance_scorecard/detalle_incidentes.html'

class IncindenteListaView(generic.ListView):
    model = Incidentes
    context_object_name = 'incidentes'
    template_name = 'balance_scorecard/lista_incidentes.html'
    queryset = Incidentes.objects.filter().order_by('fecha_incidente')



# Crud Compromisos

class CompromisosCrearView(BSModalCreateView):
    form_class = CompromisosForm
    template_name = 'balance_scorecard/registro_compromiso.html'
    success_message = 'Compromiso Creado exitosamente.'
    success_url = reverse_lazy('lista_compromisos')


class CompromisosActualizarView(BSModalUpdateView):
    model = Compromisos
    template_name = 'balance_scorecard/actualizar_compromisos.html'
    form_class = CompromisosForm
    success_message = 'Compromiso Actualizado Correctamente'
    success_url = reverse_lazy('lista_compromisos')

class CompromisosEliminarView(BSModalDeleteView):
    model = Compromisos
    template_name = 'balance_scorecard/eliminar_compromiso.html'
    success_message = 'Se ha eliminado el compromiso exitosamente.'
    success_url = reverse_lazy('index')


class CompromisosDetalleView(BSModalReadView):
    model = Compromisos
    template_name = 'balance_scorecard/detalle_compromiso.html'



def CompromisosListaView(request):
    model = Compromisos
    compromisos = Compromisos.objects.filter().order_by('fecha_plazo')
    cont = Compromisos.objects.filter().order_by('fecha_plazo').count()
    completas=0
    pendientes=0
    proceso=0
    for i in compromisos:
        if i.estado_compromiso == 1:
            completas= completas + 1
        if i.estado_compromiso == 2:
            proceso = proceso + 1
        if i.estado_compromiso == 3:
            pendientes = pendientes + 1
    return render(request,'balance_scorecard/lista_compromisos.html',{'compromisos':compromisos,'completas':completas,'pendientes':pendientes,'proceso':proceso,'fecha':FechaDia()})


#Crud Reuniones

class ReunionCrearView(BSModalCreateView):
    form_class = ReunionForm
    template_name = 'balance_scorecard/registro_reunion.html'
    success_message = 'Reunion guardada exitosamente.'
    success_url = reverse_lazy('lista_reunion')


class ReunionActualizarView(BSModalUpdateView):
    model = Reunion
    template_name = 'balance_scorecard/actualizar_reunion.html'
    form_class = ReunionForm
    success_message = 'Reunion Actualizada Correctamente'
    success_url = reverse_lazy('lista_reunion')

class ReunionEliminarView(BSModalDeleteView):
    model = Reunion
    template_name = 'balance_scorecard/eliminar_reunion.html'
    success_message = 'Se ha eliminado la reunion exitosamente.'
    success_url = reverse_lazy('index')


class ReunionDetalleView(BSModalReadView):
    model = Reunion
    template_name = 'balance_scorecard/detalle_reunion.html'

def ReunionListaView(request):
    model = Reunion
    queryset = Reunion.objects.filter().order_by('fecha_reunion')
    presente = 0
    ausentes =0
    valor = []
    for i in Reunion.objects.filter(fecha_reunion__contains= FechaNow()).order_by('fecha_reunion'):
            fecha = i.fecha_reunion
            for p in i.participantes.all():
                for u in User.objects.all():
                    if p.username == u.username:
                        presente = 1+presente
                        ausentes =  presente - User.objects.all().count()
                         
    return render(request,'balance_scorecard/lista_reunion.html',{'reunion':queryset,'presentes':presente,'ausentes':ausentes})

class DataAsistencia(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        qs_count = Reunion.objects.filter(fecha_reunion__contains= FechaNow()).order_by('fecha_reunion').count()
        usuario = []
        presente = []
        ausente = []
        porcentaje=[]
        fecha=datetime.datetime.now()
        cont=0
        username = User.objects.all()
        for u in username:
            usuario.append(u.username)
            cont = Reunion.participantes.through.objects.filter(user__username=u.username, reunion__fecha_reunion__contains=FechaNow()).count()
            presente.append(cont)
            if qs_count > 0:
                ausente.append(qs_count-cont)
                porcentaje.append(round((100*cont)/qs_count,2))
            else:
                ausente.append(0)
                porcentaje.append(0)
        data ={
            'usuario':usuario,
            'presente':presente,
            'ausente':ausente,
            'fecha':fecha,
            'porcentaje':porcentaje,
            'fecha':fecha.strftime("%B-%Y")
        }
        return Response(data)

class GraficoListaView(generic.ListView):
    model = Info_kpi
    context_object_name = 'info'
    template_name = 'balance_scorecard/grafico.html'
    queryset = Info_kpi.objects.filter(fecha_modificacion__contains=FechaNow()).order_by('fecha_modificacion')


class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request,pk, format=None):
        qs_count = Info_kpi.objects.filter(fecha_modificacion__contains=FechaNow(), indicador__id=pk).order_by('fecha_modificacion')
        item = []
        labels = []
        proyeccion = []
        meta = []
        acumulado = []
        nombre =''
        suma = 0
        medida = ''
        for q in qs_count:
            item.append(int(q.valor_kpi))
            labels.append(q.fecha_modificacion.strftime("%d-%B-%Y"))
            suma = q.valor_kpi + suma
            acumulado.append(int(suma))
            a = Acumulado_kpi.objects.get(indicador__id= q.indicador_id, fecha__contains = FechaNow())
            m = Indicador.objects.get(id= a.indicador_id)
            meta.append(int(m.meta_kpi))
            proyeccion.append(int(a.proyeccion))
            nombre = m.nombre_kpi
            medida = m.unidad_medida
        fecha=datetime.datetime.now()
        data ={
            'labels':labels,
            'default':item,
            'proyeccion':proyeccion,
            'meta':meta,
            'fecha':fecha.strftime("%d-%B-%Y"),
            'nombre':nombre,
            'acumulado':acumulado,
            'medida':medida
        }
        return Response(data)