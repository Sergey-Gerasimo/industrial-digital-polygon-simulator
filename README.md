# Микросервис симуляции производсвенного процесса 

## Какие сущности дожны быть? 
1. Поставщик
    ```protobuf 
    message Supplier { 
        string supplier_id = 1; 
        string name = 2; 
        string product_name = 3;
        int64 delivery_period = 4; 
        double reliability = 5; 
        double product_quality = 6;
    }
    ```
    Операции над ним? 
    1. Создание
    2. Удаление
    3. Изменение
    4. Получить список доступных поставщиков

2. Склад 
    ```protobuf 
    message Warehouse {
        string warehouse_id = 1; 
        int32 size = 2; 
        int32 loading = 3; 
        map<string, int32> matrerials = 4; 
    }
    ```

    Операции над ним? 
        Никаких т.к это инстанс не получаемый из бд. Изменяестя только внутри системы. read only. хранится в redis

3. Рботник
    ```protobuf 
    message Worker {
        string worker_id = 1; // id работника в БД 
        string name = 2; // имя работника
        int32 qualification = 3; // квалификация работника вообще она от 1 до 9 
        string specialty = 4; // специализация работника
        int32 sallary = 5; // ЗП сотрудника

    }
    ```

    Мы может улучшать работников. надо придумать мехнизм как это делать.
    1. Получить всех 
    2. Создать
    3. Удалить
    4. Улучшать(пока не делаем в первой версии. если будем то надо будет делать хэш)


4. Логист 
    ```protobuf
    message Logist { 
        string worker_id = 1;
        string name = 2; // наверное тут можно указать возможные улучшения. например логист на велосипеде
        int32 speed = 3; // скорость логиста в один такт
        int32 cost = 4; // стоимость внедрения
        int32 sallary = 5; // ЗП логиста
    }
    ```
    Что можем делать? 
    1. Удалять 
    2. Изменять
    3. Создавать
    4. получить всех

5. Рабочее место
    ```protobuf 
    message Workplace {
        // Виды рабочих мест храним в БД.
        // Доступные рабочие места нужны только в графе
        // Рабочее место. 
        string workplace_name = 1; 
        string required_speciality = 2; 
        string required_qualification = 3; 
        string worker_id = 4; 
        int32 step_number = 5; // порядковый номер процесса по карте технического процесса
    }
    ```
    Все необходимые процесссы хранятся в БД. Процессы формируются в графе. Сосавной тип. 

    НАДО ПОДУМАТЬ КАК ЗАДАТЬ КОНСТЕЙНЫ 

    Что можем делать? 
    1. Получить все необходимые процессы

6. Путь логиста
    ```protobuf
    message Route {
        int32 lenght = 1; 
        int8 from_workpalce = 2; 
        int8 to_workplace = 3; 
    }
    ```

    Создается на фронтенде(возможно изменим)


