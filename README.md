# Project Structure


# Enviroment
* Create and set the enviroment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
* Install the requirements:
```bash
pip install -r requirements.txt
```

### Entering
```mermaid
flowchart TD
    A[Cars is coming] -- Red --> B[Stop at the gate]
    B --> C[Camera read the plate]
    C --> D[Check if in the database]
    D -- No --> B
    D -- Yes --> E[Check if active and payment]
    E -- No --> B
    E -- Yes --> F[Open Gate]
    E -- Green --> F

    F --> G[Update parking spot counter screen]
```

```mermaid
flowchart TD
    Z[Check parkings counter] -- Empty --> A
    Z -- Full --> Z
    A[Camera read the plate] --> B[Check if match formats]
    B -- No --> A
    B -- Yes --> C[GET /plate to check if in database account_id]
    C -- No --> A
    C -- Yes --> D[GET to check if active and payment]
    D -- No --> A
    D -- Yes --> E[POST to create session]
    E --> F[Open Gate]
```


### Exiting
```mermaid
flowchart TD
    A[Cars is coming] -- Red --> B[Stop at the gate]
    B --> C[Camera read the plate]
    C --> D[Calculate the pay amount]
    D -- Green --> F[Open Gate]
```

```mermaid
flowchart TD
    A[Camera read the plate] --> B[Check if match formats]
    B -- No --> A
    B -- Yes --> C[GET /plate for account_id]
    C --> D[Open gate]
    D --> E[Send payment]
    D --> F[DELETE session]
```



# Todo 
* MQTT handler (split gate backend and MQTT)
* Handle search of correct usb port for arduino
* Model time series 
* Model correct plate's format
* Clean up OCR file from unnecessary slop
* Create the scale model
* Understand the dimension of scale model in relation to dimension of plate
* Create a single script to handle all the startup terminals
* Split the webcam input entering/exiting