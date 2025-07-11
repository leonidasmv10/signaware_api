from ..workflows.sound_detector_workflow import SoundDetectorWorkflow
from .base_agent import BaseAgent


class SoundDetectorAgent(BaseAgent):
    """
    Agente especializado para la detección de sonidos.
    Coordina el workflow de procesamiento de audio y análisis de sonidos.
    """

    def _setup_components(self):
        """Configura los componentes específicos del agente de detección de sonidos."""

        # Inicializar workflow
        self.workflow = SoundDetectorWorkflow()

        # Configurar parámetros específicos del agente
        self.supported_audio_formats = ["wav", "mp3", "mpeg", "ogg"]
        self.max_audio_size_mb = 50  # Tamaño máximo de archivo en MB

    def validate_input(self, user_input: str) -> bool:
        """
        Valida la entrada del usuario para el agente de detección de sonidos.
        Permite entrada vacía o None ya que el procesamiento se basa en archivos de audio.
        
        Args:
            user_input: Entrada del usuario a validar
            
        Returns:
            bool: True si la entrada es válida, False en caso contrario
        """
        # Para el agente de detección de sonidos, la entrada del usuario es opcional
        # ya que el procesamiento se basa en archivos de audio
        return True

    def postprocess_output(self, output) -> dict:
        """
        Postprocesa la salida del agente de detección de sonidos.
        Maneja salidas de tipo diccionario que contienen el estado final.
        
        Args:
            output: Salida del agente (puede ser dict o str)
            
        Returns:
            dict: Salida postprocesada como diccionario
        """
        # Si la salida ya es un diccionario, devolverla tal como está
        if isinstance(output, dict):
            return output
        
        # Si es una cadena, convertirla a diccionario con información básica
        if isinstance(output, str):
            return {
                "sound_type": output,
                "confidence": 0.0,
                "transcription": "",
                "messages": []
            }
        
        # Si es None o cualquier otro tipo, devolver diccionario vacío
        return {
            "sound_type": "Unknown",
            "confidence": 0.0,
            "transcription": "",
            "messages": []
        }

    def execute(self, user_input: str, **kwargs) -> dict:
        """
        Ejecuta el workflow de detección de sonidos.

        Args:
            user_input: Entrada del usuario (opcional para este agente)
            **kwargs: Argumentos adicionales que deben incluir:
                - audio_path: Ruta del archivo de audio
                - audio_file: Archivo de audio subido

        Returns:
            dict: Estado final con información del sonido detectado
        """
        try:
            # Extraer argumentos específicos
            audio_path = kwargs.get("audio_path")
            audio_file = kwargs.get("audio_file")

            # Validar argumentos requeridos
            if not audio_path and not audio_file:
                raise ValueError(
                    "Se requiere audio_path o audio_file para la detección de sonidos"
                )

            # Obtener estado inicial
            initial_state = self.workflow.get_initial_state()

            # Configurar el estado con los datos de entrada
            if audio_path:
                initial_state["audio_path"] = audio_path
            if audio_file:
                initial_state["audio_file"] = audio_file

            # Ejecutar el workflow
            final_state = self.workflow.execute(initial_state)
            return final_state

        except Exception as e:
            error_msg = f"❌ Error al clasificar intención: {e}"
            print(error_msg)
            return "GENERAL_QUERY"

    def validate_audio_file(self, audio_file) -> bool:
        """
        Valida si el archivo de audio es compatible.

        Args:
            audio_file: Archivo de audio a validar

        Returns:
            bool: True si el archivo es válido
        """
        if not audio_file:
            return False

        # Verificar tamaño
        if hasattr(audio_file, "size"):
            max_size_bytes = self.max_audio_size_mb * 1024 * 1024
            if audio_file.size > max_size_bytes:
                return False

        # Verificar formato
        if hasattr(audio_file, "name"):
            file_extension = audio_file.name.lower().split(".")[-1]
            if file_extension not in self.supported_audio_formats:
                return False

        return True

    def get_detailed_status(self) -> dict:
        """
        Obtiene información detallada del estado del agente.

        Returns:
            dict: Información detallada del agente
        """
        base_status = self.get_status()
        base_status.update(
            {
                "supported_formats": self.supported_audio_formats,
                "max_audio_size_mb": self.max_audio_size_mb,
                "workflow_initialized": self.workflow.compiled_workflow is not None,
            }
        )
        return base_status
