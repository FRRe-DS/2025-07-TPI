# portal_compras/pipeline.py
def get_email_from_keycloak(backend, details, response, user=None, *args, **kwargs):
    if user and backend.name == 'keycloak':
        # Actualizar email si viene en la respuesta
        if response.get('email') and not user.email:
            user.email = response.get('email')
            user.save()
        
        # Actualizar nombre y apellido
        if response.get('given_name') and not user.first_name:
            user.first_name = response.get('given_name')
        
        if response.get('family_name') and not user.last_name:
            user.last_name = response.get('family_name')
            
        user.save()