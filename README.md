Simulador de Digestión de ADN con IA
Pontificia Universidad Católica Madre y Maestra (PUCMM)
Escuela de Ciencias Naturales y Exactas — Laboratorio de Biología Celular y Genética (BIO211-P)


Propósito del proyecto
Este simulador interactivo permite a los estudiantes de biología molecular comprender el proceso de digestión de ADN por enzimas de restricción mediante una interfaz visual y retroalimentación generada por inteligencia artificial (IA). La aplicación forma parte de una propuesta de innovación educativa (Bono de Innovación PUCMM) que busca integrar herramientas de IA en los laboratorios virtuales para fortalecer el aprendizaje autónomo y contextualizado.


Funcionalidades principales
•	Simulación de digestión de ADN con múltiples enzimas de restricción (EcoRI, HindIII, BamHI, etc.)
•	Visualización del gel de agarosa simulado con carril marcador y digestiones combinadas
•	Retroalimentación automática con IA: el estudiante predice el número de fragmentos y la IA explica si su razonamiento es correcto
•	Generador de preguntas y respuestas personalizadas sobre el experimento
•	Tutor virtual contextual, que responde preguntas en lenguaje natural sobre los resultados
•	Panel de resultados y métricas, con indicadores de aprendizaje y adopción de IA
•	Descarga del archivo de resultados (.csv) para análisis docente


Requisitos del entorno local
1.	Instala las dependencias: pip install -r requirements.txt
2.	Crea la carpeta .streamlit y dentro un archivo secrets.toml con tu clave de OpenAI.
3.	Ejecuta la app: streamlit run app.py


Despliegue en Streamlit Cloud
La aplicación puede ejecutarse directamente desde el navegador (sin instalar nada). Enlace público:


Resultados esperados (para Bono de Innovación)

Indicador	            Descripción	                                  Meta
Uso / participación	  % de estudiantes que realizaron simulaciones  80 %
Comprensión conceptual % de aciertos en predicción de fragmentos	  70 %
Satisfacción	         Promedio de utilidad percibida (1–5)	        4.0
Adopción de IA	       % que usó tutor o preguntas IA	              60 %

Autora
 
Natalia Fernández
MSc Data Science & Artificial Intelligence — University of Liverpool Profesora, Escuela de Ciencias Naturales y Exactas — PUCMM
Email:natalia.fernandez@pucmm.edu.do


Créditos y licencia
Desarrollado como parte de la iniciativa de Innovación Educativa PUCMM 2025, con fines académicos y formativos. Uso educativo libre citando la fuente.
