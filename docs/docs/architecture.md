Architettura



ClinicalTwin è progettato secondo un’architettura a microservizi containerizzati orchestrati tramite Docker Compose, con l’obiettivo di garantire modularità, riproducibilità computazionale e separazione delle responsabilità tra i diversi componenti della pipeline di analisi neuroimaging.



Il sistema integra servizi dedicati alla gestione dell’autenticazione, orchestrazione delle elaborazioni, preprocessing MRI automatizzato, inferenza statistica, gestione dei modelli di classificazione e visualizzazione interattiva dei risultati clinici. Questa organizzazione consente l’esecuzione asincrona delle pipeline radiomiche e facilita l’estensione futura della piattaforma con nuovi moduli diagnostici.



Ogni servizio opera in modo indipendente all’interno di un container Docker, comunicando tramite API REST interne alla rete applicativa.

                        +----------------------+

&#x20;                       |      Frontend        |

&#x20;                       |   React + NiiVue     |

&#x20;                       +----------+-----------+

&#x20;                                  |

&#x20;                                  |

&#x20;                       +----------v-----------+

&#x20;                       |      API Gateway     |

&#x20;                       | FastAPI + JWT Auth   |

&#x20;                       +----------+-----------+

&#x20;                                  |

&#x20;               +------------------+------------------+

&#x20;               |                                     |

&#x20;   +-----------v-----------+             +-----------v-----------+

&#x20;   |      Orchestrator     |             |      LLM Service      |

&#x20;   |   Task coordination   |             | Spatial RAG Assistant |

&#x20;   +-----------+-----------+             +-----------------------+

&#x20;               |

&#x20;               |

&#x20;   +-----------v-----------+

&#x20;   |   Nextflow Worker     |

&#x20;   | FreeSurfer / Radiomics|

&#x20;   +-----------+-----------+

&#x20;               |

&#x20;               |

&#x20;   +-----------v-----------+

&#x20;   |     Model Service     |

&#x20;   |  MLflow + DagsHub     |

&#x20;   +-----------+-----------+

&#x20;               |

&#x20;               |

&#x20;   +-----------v-----------+

&#x20;   |   Inference Engine    |

&#x20;   |     R + UMAP + KNN    |

&#x20;   +-----------------------+

