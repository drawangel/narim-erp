Me gustaría implementar un MVP para joyerías con soporte a varias tiendas. Nuestro cliente inicial con el que tomaremos requerimientos y haremos tests se llama "IAN OR". Esta empresa tiene varias tiendas físicas, y requiere centralizar la información, manteniendo claro qué ha hecho cada tienda. 
IAN OR está operando actualmente con un software desarrollado in-house, y buscan actualizar su ERP a una plataforma actualizada. Se ha seleccionado Odoo como plataforma nueva. El MVP no incluye la migración de datos, esto se hará en una fase posterior.

Las funcionalidades con las que vamos a empezar son la de gestionar clientes y realizar compras a cliente y empeños.

# Alta de cliente
Posibilidad de crear clientes indicando sus datos personales (Nombre, Apellidos, dirección, DNI, etc.) Se requiere poder incluir fotografías del DNI del cliente (frontal y reverso)


# Compra a particular

Las compras se vinculan obligatoriamente a clientes dados de alta.
La información de una compra incluye:
- Descripción del o los artículos. Texto libre.
- Peso en gramos
- Calidad del material (valores administrados en BD). Para el oro, la letra "k" representa el kilataje: 24k, 22k, 18k, 14k, 9k, Plata, Otros
- Importe de la compra. Debe poder fijarse de forma libre para cada compra, dado que el precio del oro es muy fluctuante y puede variar en cada compra.
- Fotografías de los items que se compran.

Las compras a particulares deben poder generar un "Contrato" exportable a PDF siguiendo un diseño estandarizado (Pendiente de definir). Este documento se imprime y firma por parte de IAN OR y el cliente, y se guardará en formato físico. También debe ser posible adjuntar el documento escaneado.

# Enviar a fundición
Las compras realizadas a cliente de oro se pueden enviar a fundición. Para ello, es imprescindible que se haya superado el tiempo de bloqueo fijado por la policía. Inicialmente, el tiempo es de 14 días pero debe ser configurable. Este setup es común para todos los productos y sólo puede ser editable por un rol de administración.

El envío a fundición dará de baja el artículo en el ERP con fecha auditable.

# Empeños (Compra recuperable)

Los clientes pueden realizar un empeño en lugar de una venta en firme. Además de los datos indicados para el escenario de la compra a un particular, además se introducirá:
- Precio Compra (sustituye al precio de venta): importe que recibe el cliente en el empeño.
- Nº de Días: duración del empeño en días. Esto genera un plazo en el cual IAN OR se compromete a custodiar el artículo. 
- Margen: porcentaje que IAN OR recargará al cliente en el momento de recuperar su artículo
- Recargo: porcentaje (2 decimales) de recargo que se aplicará cada día tras superar el plazo estipulado. El recargo se calcula sobre el precio original del empeño
- Precio Recuperación: se calcula automáticamente usando el precio de compra * margen. Se muestra en la UI para facilitar el cálculo cuando el cliente viene a recuperar su artículo.

Un cliente puede recuperar su empeño pagando de vuelta el Precio de Recuperación + el recargo (si lo hubiera). 
Debe ser posible modificar el margen y recargo por parte de IAN OR en cualquier momento.

# Informe policial
Ya sea durante el tiempo de bloqueo o posterior, la policía puede solicitar la presentación de documentación de compras y empeños realizados. Para ello, IAN OR debe poder generar un informe de los productos comprados y empeñados. Esta documentación se genera en formato PDF y en Excel siguiendo templates (pendientes de definir).

# Compras a proveedor

IAN OR también puede realizar compras a proveedores. Estas compras son de artículos de joyería y relojería cuyo objetivo es la venta a cliente final. Estas compras a proveedor se realizan en global, pero pueden ser surtidas a diferentes tiendas de IAN OR.

# Ventas

Ventas de artículos a cliente final. Los artículos vendibles son aquellos que provienen de compras a proveedor, compras a cliente, o empeños que no han sido recuperados por el cliente final (IAN OR decide cuándo incluirlos en el stock vendible).

# Servicios
IAN OR también dispone de servicios. Deben poder darse de alta en el ERP. Los servicios típicos son:
- Taller: arreglos y mantenimiento de piezas de joyerías ejecutadas por personal de taller de IAN OR.
- Compostura: arreglos y mantenimiento de talleres externos. IAN OR es facturado y paga por esos servicios

# Formas de pago
El ERP debe poder soportar, como mínimo, las formas de pago: Efectivo, Tarjeta de Crédito, PayPal, Transferencia Bancaria, Bizum. Esto debe poder ser administrable.

# RBAC

La aplicación debe poder definir distintos roles y permisos asociados, de forma que algunas acciones requieran de un rol de administrador, mientras que la operativa habitual la puede hacer un rol de operador.