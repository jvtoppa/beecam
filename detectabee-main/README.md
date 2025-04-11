# Sistema de Monitoramento de Colmeias com Raspberry Pi

Este projeto integra sensores ambientais, câmera com detecção de marcadores ArUco e um sistema de visualização embarcado para monitoramento de colmeias utilizando um Raspberry Pi.

## Funcionalidades

- Leitura de sensores ambientais (temperatura, pressão, aceleração, e qualidade do ar)
- Detecção de abelhas via marcadores ArUco usando a câmera PiCamera2
- Interface OLED com troca de páginas via botão físico
- Registro dos dados em arquivos CSV com timestamp
- Atualização em tempo real das leituras na tela e via câmera

## Estrutura do Projeto

```
.
├── main.py             # Loop principal e integração geral
├── camera.py           # Captura de imagem e detecção de marcadores
├── sensors.py          # Leitura dos sensores conectados via I2C
├── screen.py           # Interface com o display OLED
├── tables.py           # Manipulação e gravação em arquivos CSV
├── configs.py          # Parâmetros globais e de configuração
└── README.md           # Documentação do projeto
```

## Requisitos

- Raspberry Pi 4 ou superior
- PiCamera2 e biblioteca `picamera2`
- Sensores: CCS811, BMP280, MPU9250
- Display OLED SSD1306
- Python 3.9+
- Bibliotecas Python:
  - `opencv-python`
  - `numpy`
  - `adafruit-circuitpython-ccs811`
  - `adafruit-circuitpython-bmp280`
  - `adafruit-circuitpython-ssd1306`
  - `smbus`, `board`, `busio`, `RPi.GPIO`, entre outros

## Instalação

1. Clone este repositório:

```bash
git clone https://github.com/seu-usuario/nome-do-projeto.git
cd nome-do-projeto
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Execute o projeto:

```bash
python3 main.py
```

## Observações

- Certifique-se de que os sensores estejam corretamente conectados ao barramento I2C.
- A câmera deve estar ativada e calibrada via `picamera2`.
