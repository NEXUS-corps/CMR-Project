create a vm for windows pythom -m venv .venv
activate vm using .\venv\Scripts\activate    
in terminal type pip install -r requirements.txt
type cd backend
type python app.py
now in a new terminal copy pase this "(Invoke-WebRequest `
>>   -Uri http://127.0.0.1:5000/predict `
>>   -Method POST `
>>   -ContentType "application/json" `
>>   -Body '{
>>     "latitude": 12.97,
>>     "longitude": 77.59
>>   }'
>> ).Content
>> "
Now you will get the prediction
