from roboflow import Roboflow

rf1 = Roboflow(api_key="OMK13lODzeEz6X1NFfoF")
project1 = rf1.workspace().project("leaf-classification-0gekz")
modelClassification = project1.version(1).model

rf2 = Roboflow(api_key="kVjiNm6VQczdBaSdhwOg")
project2 = rf2.workspace().project("healthy_pest_disease")
modelIdentification = project2.version(4).model
