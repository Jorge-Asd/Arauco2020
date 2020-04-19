from django.urls import path
from balance_scorecard import views

urlpatterns = [
    path('', views.Index, name='index'),
    path('crear/', views.IndicadorCrearView.as_view(), name='crear'),
    path('detalle/<int:pk>', views.IndicadorDetalleView.as_view(), name='detalle'),
    path('actualizar/<int:pk>', views.IndicadorActualizarView.as_view(), name='actualizar'),
    path('eliminar/<int:pk>', views.IndicadorEliminarView.as_view(), name='eliminar'),
    path('registro/', views.RegistroView.as_view(), name='registro'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('home/<int:pk>', views.Home2, name='home'),

    #Crud Informacion Kpi

    path('actualizar_info/<int:pk>', views.IndicadorActualizarInfoView.as_view(), name='actualizar_info'),
    path('crear_info/<int:pk>', views.IndicadorCrearInfoView.as_view(), name='crear_info'),

    #Crud Registro Incidentes
    path('registro_incidentes/',views.IncidentesCrearView.as_view(), name='registro_incidentes'),
    path('lista_incidentes/',views.IncindenteListaView.as_view(), name='lista_incidentes'),
    path('actualizar_incidentes/<int:pk>',views.IncidentesActualizarView.as_view(), name='actualizar_incidentes'),
    path('detalle_incidentes/<int:pk>',views.IncidenteDetalleView.as_view(), name='detalle_incidentes'),

    #Crud Registro Compromisos
    path('registro_compromiso/',views.CompromisosCrearView.as_view(), name='registro_compromiso'),
    path('actualizar_compromisos/<int:pk>',views.CompromisosActualizarView.as_view(), name='actualizar_compromisos'),
    path('lista_compromisos/',views.CompromisosListaView, name='lista_compromisos'),

    #Crud Registro Reuniones
    path('registro_reunion/',views.ReunionCrearView.as_view(), name='registro_reunion'),
    path('actualizar_reunion/<int:pk>',views.ReunionActualizarView.as_view(), name='actualizar_reunion'),
    path('lista_reunion/',views.ReunionListaView, name='lista_reunion'),

    #Crud Vista cuadro de mando
    path('balancedscorecard/<int:pk>', views.BSView,name='balancedscorecard'),
    #Reportes
    path('reporte_indicadores/', views.GeneratePdf.as_view(),name='reporte_indicadores'),
    path('reporte_asistencia/', views.PdfAsistencia.as_view(),name='reporte_asistencia'),

    path('api/asistencia/', views.DataAsistencia.as_view(),name='api-data'),
    path('api/chart/data/<int:pk>', views.ChartData.as_view(),name='api-chart'),
    path('grafico/', views.GraficoListaView.as_view(),name='grafico'),
]
    