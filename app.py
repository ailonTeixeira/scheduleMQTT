                                                                                                                                                                                                                                                                                                                                                                                                           app.py                                                                                                                                                                                                                                                                                                                                                                                                                         
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mqtt import Mqtt
from datetime import datetime
import time

estado_rele = False

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agendamentos.db'
app.config['MQTT_BROKER_URL'] = 'localhost'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_REFRESH_TIME'] = 1.0

db = SQLAlchemy(app)
mqtt = Mqtt(app)

# Modelo de dados para agendamentos
class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    acao = db.Column(db.String(10), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    executado = db.Column(db.Boolean, default=False)

@app.route('/')
def index():
    agendamentos = Agendamento.query.order_by(Agendamento.data_hora).all()
    return render_template('index.html', agendamentos=agendamentos)

# Modifique a rota /controle
@app.route('/controle', methods=['POST'])
def controle():
    global estado_rele
    estado = request.form.get('estado')
    topico = "casa/rele/controle"
    
    if estado == 'on':
        mqtt.publish(topico, 'ligar')
        estado_rele = True
    else:
        mqtt.publish(topico, 'desligar')
        estado_rele = False
    
    return jsonify({'success': True})

# Modifique a rota /estado
@app.route('/estado')
def estado():
    return jsonify({'rele': 'ligado' if estado_rele else 'desligado'})

@app.route('/agendar', methods=['POST'])
def agendar():
    data = request.form.get('data')
    hora = request.form.get('hora')
    acao = request.form.get('acao')
    
    data_hora = datetime.strptime(f"{data} {hora}", "%Y-%m-%d %H:%M")
    novo_agendamento = Agendamento(acao=acao, data_hora=data_hora)
    
    db.session.add(novo_agendamento)
    db.session.commit()
    
    return redirect(url_for('index'))

@app.route('/excluir/<int:id>')
def excluir(id):
    agendamento = Agendamento.query.get_or_404(id)
    db.session.delete(agendamento)
    db.session.commit()
    return redirect(url_for('index'))

def verificar_agendamentos():
    with app.app_context():
        while True:
            agora = datetime.now()
            agendamentos = Agendamento.query.filter(
                Agendamento.data_hora <= agora,
                Agendamento.executado == False
            ).all()

            for ag in agendamentos:
                mensagem = f"Enviando comando agendado: {ag.acao} em {ag.data_hora}"
                print(f"[DEBUG] {mensagem}")  # Log no console

                # Publica no MQTT
                topico = "casa/rele/controle"
                mqtt.publish(topico, ag.acao)

                # Atualiza no banco de dados
                ag.executado = True
                db.session.commit()

                # Remove após execução (opcional)
                db.session.delete(ag)
                db.session.commit()

                # Log de confirmação
                print(f"[DEBUG] Comando {ag.acao} enviado com sucesso para o ESP32")

            time.sleep(60)  # Verifica a cada minuto

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Inicia thread para verificar agendamentos
    import threading
    thread = threading.Thread(target=verificar_agendamentos)
    thread.daemon = True
    thread.start()
    
    app.run(host='0.0.0.0', port=5004, debug=True)
