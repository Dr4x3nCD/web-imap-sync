from flask import Flask, render_template, request, redirect, url_for, Response, session, jsonify
import subprocess
import time
import uuid
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "x3QT3mibCQAf8Ue6a6628sNU6Nz33y6Wp36NtcXGN33jruZdP6"
app.config['UPLOAD_FOLDER'] = '/tmp/imapsync_uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    form_data = session.get('form_data')
    return render_template('index.html', form_data=form_data)


@app.route('/clear_config')
def clear_config():
    session.pop('form_data', None)
    return redirect(url_for('index'))


def detect_imap_settings(email):
    """
    Auto-detect IMAP settings based on email address.
    Returns dict with 'host' and 'port' or None if detection fails.
    """
    if not email or '@' not in email:
        return None
    
    domain = email.split('@')[1].lower()
    
    # Common IMAP configurations
    common_configs = {
        'gmail.com': {'host': 'imap.gmail.com', 'port': '993'},
        'googlemail.com': {'host': 'imap.gmail.com', 'port': '993'},
        'outlook.com': {'host': 'outlook.office365.com', 'port': '993'},
        'hotmail.com': {'host': 'outlook.office365.com', 'port': '993'},
        'live.com': {'host': 'outlook.office365.com', 'port': '993'},
        'office365.com': {'host': 'outlook.office365.com', 'port': '993'},
        'yahoo.com': {'host': 'imap.mail.yahoo.com', 'port': '993'},
        'yahoo.fr': {'host': 'imap.mail.yahoo.com', 'port': '993'},
        'aol.com': {'host': 'imap.aol.com', 'port': '993'},
        'icloud.com': {'host': 'imap.mail.me.com', 'port': '993'},
        'me.com': {'host': 'imap.mail.me.com', 'port': '993'},
        'mac.com': {'host': 'imap.mail.me.com', 'port': '993'},
        'zoho.com': {'host': 'imap.zoho.com', 'port': '993'},
    }
    
    # Check if domain is in common configs
    if domain in common_configs:
        return common_configs[domain]
    
    # Try common patterns
    possible_hosts = [
        f'imap.{domain}',
        f'mail.{domain}',
        domain
    ]
    
    # Return the first pattern (we'll test it)
    return {'host': possible_hosts[0], 'port': '993'}

@app.route('/test_connection', methods=['POST'])
def test_connection():
    try:
        detected_settings = {}
        
        # Helper to get value
        def get_val(key):
            return request.form.get(key)
        
        # Auto-detect settings if host is missing
        host1 = get_val('host1')
        user1 = get_val('user1')
        if not host1 and user1:
            settings = detect_imap_settings(user1)
            if settings:
                host1 = settings['host']
                detected_settings['host1'] = host1
                if not get_val('port1'):
                    detected_settings['port1'] = settings['port']
        
        host2 = get_val('host2')
        user2 = get_val('user2')
        if not host2 and user2:
            settings = detect_imap_settings(user2)
            if settings:
                host2 = settings['host']
                detected_settings['host2'] = host2
                if not get_val('port2'):
                    detected_settings['port2'] = settings['port']
        
        # Test each host separately for better error reporting
        results = {'host1': None, 'host2': None}
        
        def test_single_host(host_num):
            """Test a single host connection"""
            cmd = ["./imapsync"]
            
            def add_arg(key, val):
                if val:
                    cmd.extend([f"--{key}", val])
            
            def add_bool(key):
                if request.form.get(key):
                    cmd.append(f"--{key}")
            
            # Add host-specific parameters
            if host_num == 1:
                add_arg('host1', host1)
                add_arg('user1', user1)
                add_arg('port1', detected_settings.get('port1') or get_val('port1'))
                add_arg('password1', get_val('password1'))
                add_arg('authmech1', get_val('authmech1'))
                add_arg('authuser1', get_val('authuser1'))
                add_arg('oauthaccesstoken1', get_val('oauthaccesstoken1'))
                add_bool('ssl1')
                add_arg('timeout1', get_val('timeout1') or '30')
                
                # Use same credentials for host2 (dummy test)
                add_arg('host2', host1)
                add_arg('user2', user1)
                add_arg('port2', detected_settings.get('port1') or get_val('port1'))
                add_arg('password2', get_val('password1'))
                add_bool('ssl2')
                add_arg('timeout2', get_val('timeout1') or '30')
            else:
                # Use same credentials for host1 (dummy test)
                add_arg('host1', host2)
                add_arg('user1', user2)
                add_arg('port1', detected_settings.get('port2') or get_val('port2'))
                add_arg('password1', get_val('password2'))
                add_bool('ssl1')
                add_arg('timeout1', get_val('timeout2') or '30')
                
                # Add host2 parameters
                add_arg('host2', host2)
                add_arg('user2', user2)
                add_arg('port2', detected_settings.get('port2') or get_val('port2'))
                add_arg('password2', get_val('password2'))
                add_arg('authmech2', get_val('authmech2'))
                add_arg('authuser2', get_val('authuser2'))
                add_arg('oauthaccesstoken2', get_val('oauthaccesstoken2'))
                add_bool('ssl2')
                add_arg('timeout2', get_val('timeout2') or '30')
            
            # Handle passfiles
            if host_num == 1:
                file1 = request.files.get('passfile1')
                if file1 and file1.filename:
                    filename = secure_filename(file1.filename)
                    path = os.path.join(app.config['UPLOAD_FOLDER'], f"test_{uuid.uuid4()}_{filename}")
                    file1.save(path)
                    cmd.extend(['--passfile1', path])
                    cmd.extend(['--passfile2', path])
            else:
                file2 = request.files.get('passfile2')
                if file2 and file2.filename:
                    filename = secure_filename(file2.filename)
                    path = os.path.join(app.config['UPLOAD_FOLDER'], f"test_{uuid.uuid4()}_{filename}")
                    file2.save(path)
                    cmd.extend(['--passfile1', path])
                    cmd.extend(['--passfile2', path])
            
            cmd.append('--justlogin')
            
            # Run process
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            stdout, _ = process.communicate()
            
            return {
                'success': process.returncode == 0,
                'output': stdout,
                'returncode': process.returncode
            }
        
        # Test Host1 if provided
        if host1 and user1:
            results['host1'] = test_single_host(1)
        
        # Test Host2 if provided
        if host2 and user2:
            results['host2'] = test_single_host(2)
        
        # Build response message
        response = {}
        if detected_settings:
            response['detected_settings'] = detected_settings
        
        messages = []
        all_success = True
        
        if results['host1']:
            if results['host1']['success']:
                messages.append("✅ HOST1 (Source): Connexion RÉUSSIE !")
            else:
                all_success = False
                messages.append("❌ HOST1 (Source): Échec de connexion")
                # Extract error details
                output = results['host1']['output']
                if "Authentication failed" in output or "AUTHENTICATIONFAILED" in output:
                    messages.append("   → Identifiants incorrects (vérifiez email/mot de passe)")
                elif "timeout" in output.lower():
                    messages.append("   → Le serveur ne répond pas (Timeout)")
                elif "socket" in output.lower() or "refused" in output.lower():
                    messages.append("   → Connexion refusée (vérifiez host/port)")
        
        if results['host2']:
            if results['host2']['success']:
                messages.append("✅ HOST2 (Destination): Connexion RÉUSSIE !")
            else:
                all_success = False
                messages.append("❌ HOST2 (Destination): Échec de connexion")
                # Extract error details
                output = results['host2']['output']
                if "Authentication failed" in output or "AUTHENTICATIONFAILED" in output:
                    messages.append("   → Identifiants incorrects (vérifiez email/mot de passe)")
                elif "timeout" in output.lower():
                    messages.append("   → Le serveur ne répond pas (Timeout)")
                elif "socket" in output.lower() or "refused" in output.lower():
                    messages.append("   → Connexion refusée (vérifiez host/port)")
        
        final_message = "\n".join(messages)
        
        if detected_settings:
            final_message += "\n\n✨ Paramètres auto-détectés :\n"
            for key, val in detected_settings.items():
                final_message += f"- {key}: {val}\n"
        
        response.update({
            "status": "success" if all_success else "error",
            "message": final_message
        })
        
        return jsonify(response)

    except Exception as e:
        return jsonify({"status": "error", "message": f"Erreur interne lors du test : {str(e)}"})

import csv
import io

import threading
import time

# Global storage for tasks (in-memory for simplicity, could be DB/Redis)
TASKS = {}

@app.route('/migrate', methods=['POST'])
def migrate():
    # Store form data in session for "Back to config"
    session['form_data'] = request.form.to_dict()

    commands = []
    
    # Helper to build a single command
    def build_command(row_data=None):
        cmd = ["./imapsync"]
        
        # Helper to get value from CSV row or Form
        def get_val(key, form_key=None):
            if row_data and key in row_data and row_data[key]:
                return row_data[key]
            return request.form.get(form_key or key)

        # Helper to add args
        def add_arg(key, form_key=None):
            val = get_val(key, form_key)
            if val:
                cmd.extend([f"--{key}", val])

        def add_bool(key):
            # Boolean flags are usually global settings from the form
            if request.form.get(key):
                cmd.append(f"--{key}")

        # Global Flags
        if request.form.get('dry'): cmd.append('--dry')
        
        # Host 1
        add_arg('host1')
        add_arg('user1')
        add_arg('port1')
        add_arg('password1')
        add_arg('authmech1')
        add_arg('authuser1')
        add_arg('oauthaccesstoken1')
        add_bool('ssl1')
        
        # Passfile 1 (Global only for now)
        file1 = request.files.get('passfile1')
        if file1 and file1.filename:
            filename = secure_filename(file1.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
            file1.save(path)
            cmd.extend(['--passfile1', path])

        # Host 2
        add_arg('host2')
        add_arg('user2')
        add_arg('port2')
        add_arg('password2')
        add_arg('authmech2')
        add_arg('authuser2')
        add_arg('oauthaccesstoken2')
        add_arg('oauthaccesstoken2')
        add_bool('ssl2')

        # Prefixes
        add_arg('prefix1')
        add_arg('prefix2')

        # Passfile 2
        file2 = request.files.get('passfile2')
        if file2 and file2.filename:
            filename = secure_filename(file2.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
            file2.save(path)
            cmd.extend(['--passfile2', path])

        # Folders
        add_arg('folder')
        add_arg('include')
        add_arg('exclude')
        add_arg('f1f2')
        add_arg('f1f2')
        add_bool('automap')
        add_bool('skipemptyfolders')
        add_bool('folderrec')
        add_bool('subscribe')

        # Filters & Messages
        add_arg('maxage')
        add_arg('minage')
        add_arg('maxsize')
        add_arg('search')
        add_arg('regexmess')
        add_arg('pipemess')
        add_bool('skipmess')
        if request.form.get('useheader_message_id'):
            cmd.extend(['--useheader', 'Message-ID'])

        # Performance
        add_arg('maxmessagespersecond')
        add_arg('maxbytespersecond')
        add_arg('maxsleep')
        add_bool('nofoldersizes')
        add_bool('usecache')
        add_bool('useuid')

        # Advanced
        add_arg('timeout1')
        add_arg('timeout2')
        add_bool('synclabels')
        add_bool('resynclabels')
        add_bool('syncacls')
        add_bool('resyncflags')
        add_arg('regexflag')

        # Danger / Logs
        add_bool('delete1')
        add_bool('expunge1')
        add_bool('delete2')
        add_bool('delete2folders')
        add_bool('delete2duplicates')
        
        add_bool('debug')
        add_arg('logfile')
        add_arg('emailreport1')
        add_arg('errorsmax')
        
        return cmd

    # Check Mode
    mode = request.form.get('mode')
    
    if mode == 'batch':
        csv_file = request.files.get('batch_csv')
        if csv_file:
            stream = io.StringIO(csv_file.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.DictReader(stream)
            for row in csv_input:
                row = {k.strip(): v.strip() for k, v in row.items() if k}
                commands.append(build_command(row))
    else:
        commands.append(build_command())

    # Generate Task ID
    task_id = str(uuid.uuid4())
    
    # Check Background Mode
    is_background = request.form.get('background_mode') == 'on'
    
    TASKS[task_id] = {
        'commands': commands,
        'status': 'pending',
        'logs': [],
        'created_at': time.time()
    }

    if is_background:
        # Start background thread
        thread = threading.Thread(target=run_task, args=(task_id,))
        thread.start()
        return render_template('task_started.html', task_id=task_id)
    else:
        # Store in session for immediate stream
        session['task_id'] = task_id
        # Start thread anyway to unify logic, but redirect to stream
        thread = threading.Thread(target=run_task, args=(task_id,))
        thread.start()
        return redirect(url_for('results', task_id=task_id))

import re

def analyze_log(log_text):
    issues = []
    
    # Check for 0 folders synced
    if "Folders synced                          : 0/0 synced" in log_text:
        # Check if prefix was already used in the command
        prefix1_used = re.search(r"--prefix1\s+['\"]?([^'\"\s]+)['\"]?", log_text)
        prefix2_used = re.search(r"--prefix2\s+['\"]?([^'\"\s]+)['\"]?", log_text)

        # Check for prefix mismatch clues
        p1_match = re.search(r"Host1: guessing prefix from folder listing: \[(.*?)\]", log_text)
        p2_match = re.search(r"Host2: guessing prefix from folder listing: \[(.*?)\]", log_text)
        
        suggestion = {}
        msg = "Aucun dossier n'a été synchronisé. "
        title = "Problème de Structure"
        
        # Analyze Host 1 Prefix
        if p1_match and p1_match.group(1):
             guessed_prefix = p1_match.group(1)
             
             if prefix1_used and prefix1_used.group(1) == guessed_prefix:
                 # We used it, but it failed. Suggest removing it?
                 msg += f"Le préfixe source '{guessed_prefix}' a été utilisé mais n'a pas résolu le problème. Essayez de le retirer."
                 suggestion['prefix1'] = ''
                 title = "Préfixe Source Inefficace"
             elif not prefix1_used:
                 # We didn't use it, suggest it
                 msg += f"Le serveur source semble utiliser le préfixe '{guessed_prefix}'. Essayez de le configurer."
                 suggestion['prefix1'] = guessed_prefix
                 # Also suggest an include pattern to be explicit and helpful
                 base_folder = guessed_prefix.rstrip('.')
                 suggestion['include'] = f"^{base_folder}.*"
                 title = "Préfixe Source Manquant"

        # Analyze Host 2 Prefix
        if p2_match and p2_match.group(1):
             guessed_prefix = p2_match.group(1)
             
             if prefix2_used and prefix2_used.group(1) == guessed_prefix:
                 msg += f" Le préfixe dest '{guessed_prefix}' a été utilisé sans succès."
                 suggestion['prefix2'] = ''
             elif not prefix2_used:
                 msg += f" Le serveur destination semble utiliser le préfixe '{guessed_prefix}'."
                 suggestion['prefix2'] = guessed_prefix
                 if title == "Problème de Structure": title = "Préfixe Destination Manquant"
        
        # Check for Include/Exclude conflicts
        include_used = re.search(r"--include\s+['\"]?([^'\"\s]+)['\"]?", log_text)
        if include_used:
            msg += "\n\n⚠️ Un filtre d'inclusion est actif. Il est possible qu'il exclue tous les dossiers trouvés."
            msg += " Essayez de le désactiver."
            suggestion['include'] = ''
            title = "Conflit de Filtres Possible"

        # Suggest default exclude if empty and we are suggesting things
        if suggestion and not re.search(r"--exclude", log_text):
             suggestion['exclude'] = "Trash|Junk|Spam|Corbeille"

        if not suggestion:
            msg += "Vérifiez les filtres (include/exclude) ou le mapping manuel."

        issues.append({
            "type": "prefix_issue",
            "title": title,
            "message": msg,
            "suggestion": suggestion
        })

    # Check for Auth failures
    if "Authentication failed" in log_text or "LOGIN failed" in log_text:
        issues.append({
            "type": "auth_issue",
            "title": "Échec d'authentification",
            "message": "Vérifiez vos identifiants et mots de passe.",
            "suggestion": None
        })
        
    return issues

def run_task(task_id):
    task = TASKS.get(task_id)
    if not task: return

    task['status'] = 'running'
    commands = task['commands']
    total = len(commands)

    def log(msg):
        task['logs'].append(msg)

    try:
        for i, cmd in enumerate(commands):
            log(f"--- Démarrage Compte {i+1}/{total} ---")
            
            # Mask passwords
            safe_cmd = []
            skip_next = False
            for arg in cmd:
                if skip_next:
                    skip_next = False
                    continue
                if arg in ['--password1', '--password2']:
                    safe_cmd.extend([arg, '****'])
                    skip_next = True
                else:
                    safe_cmd.append(arg)
            
            log(f"Commande: {' '.join(safe_cmd)}")

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            for line in process.stdout:
                log(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                log(f"[SUCCÈS] Compte {i+1} terminé.")
            else:
                log(f"[ERREUR] Compte {i+1} terminé avec code {process.returncode}.")
        
        task['status'] = 'completed'
        log("[Terminé] Tous les comptes ont été traités.")
        
        # Analyze logs
        full_log = "\n".join(task['logs'])
        task['analysis'] = analyze_log(full_log)

    except Exception as e:
        task['status'] = 'failed'
        log(f"[CRITIQUE] Erreur: {str(e)}")

@app.route('/task_analysis/<task_id>')
def task_analysis(task_id):
    task = TASKS.get(task_id)
    if not task: return jsonify([])
    return jsonify(task.get('analysis', []))

@app.route('/apply_fix/<task_id>')
def apply_fix(task_id):
    task = TASKS.get(task_id)
    if not task or not task.get('analysis'):
        return redirect(url_for('index'))
    
    # Apply suggestions from the first issue that has them
    form_data = session.get('form_data', {})
    for issue in task['analysis']:
        if issue.get('suggestion'):
            for key, val in issue['suggestion'].items():
                form_data[key] = val
    
    session['form_data'] = form_data
    
    # Determine which tab to open
    active_tab = 'connexion' # default
    for issue in task['analysis']:
        if issue.get('suggestion'):
            if 'prefix1' in issue['suggestion'] or 'prefix2' in issue['suggestion']:
                active_tab = 'dossiers'
            # Add more conditions here if needed
            
    return redirect(url_for('index', active_tab=active_tab))

@app.route('/results')
@app.route('/results/<task_id>')
def results(task_id=None):
    if not task_id:
        task_id = session.get('task_id')
    return render_template('results.html', task_id=task_id)

@app.route('/stream/<task_id>')
def stream(task_id):
    def generate():
        task = TASKS.get(task_id)
        if not task:
            yield "data: Erreur: Tâche introuvable.\n\n"
            return

        # Stream existing logs first
        current_idx = 0
        while True:
            if current_idx < len(task['logs']):
                yield f"data: {task['logs'][current_idx]}\n\n"
                current_idx += 1
            elif task['status'] in ['completed', 'failed']:
                break
            else:
                time.sleep(0.5)
        
        yield "data: [Fin du flux]\n\n"

    return Response(generate(), mimetype="text/event-stream")

@app.route('/track', methods=['GET', 'POST'])
def track():
    if request.method == 'POST':
        task_id = request.form.get('task_id')
        if task_id in TASKS:
            return redirect(url_for('results', task_id=task_id))
        else:
            return render_template('track.html', error="Tâche introuvable")
    return render_template('track.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
