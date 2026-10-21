from flask import Flask, render_template, request
from src.model.incapacidad import calcular_pago_incapacidad
    
app = Flask(__name__)

@app.route('/')
def incapacidad_form():
    return render_template('incapacidad.html')

@app.route('/incapacidad/calcular', methods=['POST'])
def incapacidad_calcular():
    try:
        salario = float(request.form.get('salario', ''))
        dias = float(request.form.get('dias', ''))
        pago = calcular_pago_incapacidad(salario, dias)
    except (TypeError, ValueError) as error:
        # float('abc') lanza ValueError; la función lanza TypeError/ValueError
        return render_template('incapacidad.html', error=str(error)), 400

    return render_template('resultado_incapacidad.html',
                           salario=salario, dias=dias, pago=pago)