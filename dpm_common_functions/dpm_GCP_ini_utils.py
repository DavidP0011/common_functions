# __________________________________________________________________________________________________________________________________________________________
# _ini_authenticate_API
# __________________________________________________________________________________________________________________________________________________________
def _ini_authenticate_API(config: dict, project_id: str):
    """
    Autentica utilizando el diccionario común en config.
    
    Dependiendo de 'ini_environment_identificated' se utiliza:
      - "LOCAL": usa la key "json_keyfile_local"
      - "COLAB": usa la key "json_keyfile_colab"
      - Para GCP (por ejemplo, "COLAB_ENTERPRISE" o un project_id): usa "json_keyfile_GCP_secret_id"
      
    Args:
      config (dict): Diccionario de configuración.
      project_id (str): ID del proyecto GCP (se usa en la autenticación GCP).
      
    Returns:
      Credentials: Objeto de credenciales para la autenticación.
    """
    from google.oauth2 import service_account
    env = config.get("ini_environment_identificated", "COLAB")
    if env == "LOCAL":
        json_path = config.get("json_keyfile_local")
        if not json_path:
            raise ValueError("[AUTHENTICATION ERROR ❌] Falta 'json_keyfile_local' en config para entorno LOCAL.")
        credentials = service_account.Credentials.from_service_account_file(json_path)
    elif env == "COLAB":
        json_path = config.get("json_keyfile_colab")
        if not json_path:
            raise ValueError("[AUTHENTICATION ERROR ❌] Falta 'json_keyfile_colab' en config para entorno COLAB.")
        credentials = service_account.Credentials.from_service_account_file(json_path)
    else:
        secret_id = config.get("json_keyfile_GCP_secret_id")
        if not secret_id:
            raise ValueError("[AUTHENTICATION ERROR ❌] Falta 'json_keyfile_GCP_secret_id' en config para entornos GCP.")
        from google.cloud import secretmanager
        client_sm = secretmanager.SecretManagerServiceClient()
        secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client_sm.access_secret_version(name=secret_name)
        secret_str = response.payload.data.decode("UTF-8")
        import json
        secret_info = json.loads(secret_str)
        credentials = service_account.Credentials.from_service_account_info(secret_info)
    return credentials














# __________________________________________________________________________________________________________________________________________________________
# ini_environment_identification
# __________________________________________________________________________________________________________________________________________________________
def ini_environment_identification() -> str:
    """
    Detecta el entorno de ejecución original basado en variables de entorno y módulos disponibles.

    La función utiliza la siguiente lógica:
      - Si la variable de entorno 'VERTEX_PRODUCT' tiene el valor 'COLAB_ENTERPRISE', se asume que se está ejecutando en Colab Enterprise y se devuelve ese valor original.
      - Si la variable de entorno 'GOOGLE_CLOUD_PROJECT' existe, se asume que se está ejecutando en GCP y se devuelve su valor original.
      - Si se puede importar el módulo 'google.colab', se asume que se está ejecutando en Colab (estándar) y se devuelve 'COLAB'.
      - Si ninguna de las condiciones anteriores se cumple, se asume que el entorno es Local y se devuelve 'LOCAL'.

    Returns:
        str: Cadena que representa el entorno de ejecución original. Los posibles valores son:
             - 'COLAB_ENTERPRISE'
             - El valor de la variable 'GOOGLE_CLOUD_PROJECT' (ej.: 'mi-proyecto')
             - 'COLAB'
             - 'LOCAL'
    """
    import os

    # ────────────────────────────── DETECCIÓN DEL ENTORNO ──────────────────────────────
    # Verificar si se está en Colab Enterprise / VERTEX_PRODUCT
    if os.environ.get('VERTEX_PRODUCT') == 'COLAB_ENTERPRISE':
        return os.environ.get('VERTEX_PRODUCT')
    
    # Verificar si se está en un entorno GCP (Google Cloud Platform)
    if os.environ.get('GOOGLE_CLOUD_PROJECT'):
        return os.environ.get('GOOGLE_CLOUD_PROJECT')
    
    # Verificar si se está en Colab estándar
    try:
        import google.colab  # type: ignore
        return 'COLAB'
    except ImportError:
        pass

    # Por defecto, se asume que se está en un entorno local
    return 'LOCAL'














# __________________________________________________________________________________________________________________________________________________________
# environment_identification
# __________________________________________________________________________________________________________________________________________________________
def ini_google_drive_instalation(params: dict) -> None:
    """
    Monta Google Drive en función del entorno de ejecución especificado en params.

    Args:
        params (dict):
            - entorno_identificado_str (str): Valor que indica el entorno de ejecución.
              Los posibles valores pueden ser:
                * 'VERTEX_PRODUCT'
                * 'COLAB'
                * Cualquier otro valor que indique un entorno diferente (por ejemplo, el nombre de un proyecto GCP o 'LOCAL').

    Returns:
        None

    Raises:
        ValueError: Si falta la key 'entorno_identificado_str' en params.
    """
    entorno_identificado_str = params.get('entorno_identificado_str')
    if not entorno_identificado_str:
        raise ValueError("[VALIDATION [ERROR ❌]] Falta la key 'entorno_identificado_str' en params.")

    # Montar Google Drive si el entorno es Colab (estándar o Enterprise)
    if entorno_identificado_str in ['COLAB']:
        try:
            from google.colab import drive
            drive.mount('/content/drive')
            print("[INFO ℹ️] Google Drive montado correctamente.", flush=True)
        except ImportError as e:
            print(f"[ERROR ❌] No se pudo importar google.colab para montar Google Drive: {e}", flush=True)
    else:
        print(f"[INFO ℹ️] El entorno '{entorno_identificado_str}' no requiere montaje de Google Drive.", flush=True)
