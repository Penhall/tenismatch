graph TD
    %% Dependências principais
    Django --> Users
    Django --> Profiles
    Django --> Matching
    Django --> TenisAdmin
    
    %% Dependências entre módulos
    Users -->|depende de| Profiles
    Matching -->|depende de| Profiles
    TenisAdmin -->|depende de| Matching
    TenisAdmin -->|depende de| Users
    
    %% Dependências externas
    subgraph Externas
        Django[Django Framework]
        Decouple[python-decouple]
        ML[ML Libraries]
    end
    
    %% Dependências de ML
    TenisAdmin -->|usa| ML
    Matching -->|usa| ML
    
    %% Legenda
    classDef core fill:#f96,stroke:#333,stroke-width:4px;
    classDef external fill:#6f9,stroke:#333,stroke-width:4px;
    classDef internal fill:#9cf,stroke:#333,stroke-width:4px;
    class Django,Decouple,ML external;
    class Users,Profiles,Matching,TenisAdmin internal;
```

### Explicação do Diagrama

- **Dependências Externas** (retângulos verdes):
  - `Django`: Framework principal
  - `Decouple`: Gerenciamento de configurações
  - `ML`: Bibliotecas de machine learning

- **Módulos Internos** (retângulos azuis):
  - `users`: Autenticação e permissões
  - `profiles`: Dados dos usuários
  - `matching`: Sistema de matching
  - `tenis_admin`: Administração do sistema

- **Setas**: Indicam a direção das dependências
