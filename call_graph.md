graph TD
    %% Módulos principais
    Users[users] -->|autentica| Profiles[profiles]
    Users -->|cria| Matching[matching]
    Profiles -->|fornece dados| Matching
    TenisAdmin[tenis_admin] -->|gerencia| Matching
    TenisAdmin -->|monitora| Profiles
    
    %% Fluxos principais
    subgraph Autenticação
        Users -->|login| Auth[Autenticação]
        Auth -->|redireciona| Profiles
    end
    
    subgraph Matching
        Matching -->|analisa| ML[ML Services]
        ML -->|recomenda| Matching
    end
    
    subgraph Admin
        TenisAdmin -->|treina| ML
        TenisAdmin -->|monitora| Metrics[Métricas]
    end
    
    %% Legenda
    classDef module fill:#f9f,stroke:#333,stroke-width:4px;
    classDef flow fill:#bbf,stroke:#333,stroke-width:2px;
    class Users,Profiles,Matching,TenisAdmin module;
    class Auth,ML,Metrics flow;
```

### Explicação do Diagrama

- **Módulos** (retângulos coloridos):
  - `users`: Gerencia autenticação e permissões
  - `profiles`: Armazena dados dos usuários
  - `matching`: Realiza o matching entre perfis
  - `tenis_admin`: Gerencia todo o sistema

- **Fluxos** (retângulos azuis):
  - `Autenticação`: Fluxo de login e permissões
  - `Matching`: Processo de análise e recomendação
  - `Admin`: Gerenciamento e monitoramento do sistema

- **Setas**: Indicam a direção das chamadas e dependências
