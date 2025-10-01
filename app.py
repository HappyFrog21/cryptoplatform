from flask import Flask, render_template_string, request, jsonify
import plotly.graph_objects as go
from collections import Counter
import string
import json

app = Flask(__name__)

# ========== ТВОИ ФУНКЦИИ ШИФРОВАНИЯ ==========

def caesar_cipher(text, shift, mode='encrypt'):
    """
    Шифр Цезаря - сдвигает каждую букву на заданное количество позиций в алфавите
    """
    russian_lower = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
    russian_upper = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    english_lower = string.ascii_lowercase
    english_upper = string.ascii_uppercase

    if mode == 'decrypt':
        shift = -shift

    result = []
    for char in text:
        if char in russian_lower:
            idx = russian_lower.index(char)
            new_idx = (idx + shift) % len(russian_lower)
            result.append(russian_lower[new_idx])
        elif char in russian_upper:
            idx = russian_upper.index(char)
            new_idx = (idx + shift) % len(russian_upper)
            result.append(russian_upper[new_idx])
        elif char in english_lower:
            idx = english_lower.index(char)
            new_idx = (idx + shift) % len(english_lower)
            result.append(english_lower[new_idx])
        elif char in english_upper:
            idx = english_upper.index(char)
            new_idx = (idx + shift) % len(english_upper)
            result.append(english_upper[new_idx])
        else:
            result.append(char)
    return ''.join(result)

def atbash_cipher(text):
    """
    Шифр Атбаш - заменяет первую букву алфавита на последнюю, вторую на предпоследнюю и т.д.
    """
    russian_lower = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
    russian_upper = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    english_lower = string.ascii_lowercase
    english_upper = string.ascii_uppercase

    russian_lower_reversed = russian_lower[::-1]
    russian_upper_reversed = russian_upper[::-1]
    english_lower_reversed = english_lower[::-1]
    english_upper_reversed = english_upper[::-1]

    result = []
    for char in text:
        if char in russian_lower:
            idx = russian_lower.index(char)
            result.append(russian_lower_reversed[idx])
        elif char in russian_upper:
            idx = russian_upper.index(char)
            result.append(russian_upper_reversed[idx])
        elif char in english_lower:
            idx = english_lower.index(char)
            result.append(english_lower_reversed[idx])
        elif char in english_upper:
            idx = english_upper.index(char)
            result.append(english_upper_reversed[idx])
        else:
            result.append(char)
    return ''.join(result)

def vigenere_cipher(text, key, mode='encrypt'):
    """
    Шифр Виженера - полиалфавитный шифр подстановки с использованием ключевого слова
    """
    if not key:
        return text

    russian_lower = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
    russian_upper = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    english_lower = string.ascii_lowercase
    english_upper = string.ascii_uppercase

    key_normalized = key.lower().replace('ё', 'е')
    key_clean = ''.join([
        c for c in key_normalized if c in russian_lower or c in english_lower
    ])

    if not key_clean:
        return text

    result = []
    key_index = 0

    for char in text:
        char_normalized = char
        if char == 'ё':
            char_normalized = 'е'
        elif char == 'Ё':
            char_normalized = 'Е'

        if char_normalized in russian_lower:
            alphabet_lower = russian_lower
            alphabet_upper = russian_upper
            is_upper = False
        elif char_normalized in russian_upper:
            alphabet_lower = russian_lower
            alphabet_upper = russian_upper
            is_upper = True
        elif char_normalized in english_lower:
            alphabet_lower = english_lower
            alphabet_upper = english_upper
            is_upper = False
        elif char_normalized in english_upper:
            alphabet_lower = english_lower
            alphabet_upper = english_upper
            is_upper = True
        else:
            result.append(char)
            continue

        key_char = key_clean[key_index % len(key_clean)]
        if key_char in russian_lower:
            key_alphabet = russian_lower
        else:
            key_alphabet = english_lower

        shift = key_alphabet.index(key_char)

        if mode == 'decrypt':
            shift = -shift

        if is_upper:
            idx = alphabet_upper.index(char_normalized)
            new_idx = (idx + shift) % len(alphabet_upper)
            result.append(alphabet_upper[new_idx])
        else:
            idx = alphabet_lower.index(char_normalized)
            new_idx = (idx + shift) % len(alphabet_lower)
            result.append(alphabet_lower[new_idx])

        key_index += 1

    return ''.join(result)

def caesar_brute_force(text):
    """
    Автоматический взлом шифра Цезаря методом перебора всех возможных сдвигов
    """
    russian_lower = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
    english_lower = string.ascii_lowercase

    has_russian = False
    has_english = False

    for char in text.lower():
        if char in russian_lower:
            has_russian = True
        elif char in english_lower:
            has_english = True
        if has_russian and has_english:
            break

    if not has_russian and not has_english:
        return []

    results = []

    if has_russian:
        for shift in range(1, len(russian_lower)):
            decrypted = caesar_cipher(text, shift, mode='decrypt')
            results.append((shift, decrypted, 'RU'))

    if has_english and not has_russian:
        for shift in range(1, len(english_lower)):
            decrypted = caesar_cipher(text, shift, mode='decrypt')
            results.append((shift, decrypted, 'EN'))

    return results

# ========== ЧАСТОТНЫЙ АНАЛИЗ ==========

RUSSIAN_REFERENCE_FREQ = {
    'о': 10.97, 'е': 8.45, 'а': 8.01, 'и': 7.35, 'н': 6.70, 'т': 6.26,
    'с': 5.47, 'р': 4.73, 'в': 4.54, 'л': 4.40, 'к': 3.49, 'м': 3.21,
    'д': 2.98, 'п': 2.81, 'у': 2.62, 'я': 2.01, 'ы': 1.90, 'ь': 1.74,
    'г': 1.70, 'з': 1.65, 'б': 1.59, 'ч': 1.44, 'й': 1.21, 'х': 0.97,
    'ж': 0.94, 'ш': 0.73, 'ю': 0.64, 'ц': 0.48, 'щ': 0.36, 'э': 0.32,
    'ф': 0.26, 'ъ': 0.04
}

ENGLISH_REFERENCE_FREQ = {
    'e': 12.70, 't': 9.06, 'a': 8.17, 'o': 7.51, 'i': 6.97, 'n': 6.75,
    's': 6.33, 'h': 6.09, 'r': 5.99, 'd': 4.25, 'l': 4.03, 'c': 2.78,
    'u': 2.76, 'm': 2.41, 'w': 2.36, 'f': 2.23, 'g': 2.02, 'y': 1.97,
    'p': 1.93, 'b': 1.29, 'v': 0.98, 'k': 0.77, 'j': 0.15, 'x': 0.15,
    'q': 0.10, 'z': 0.07
}

def frequency_analysis(text):
    """
    Частотный анализ текста - подсчитывает частоту встречаемости каждой буквы
    """
    text_lower = text.lower()
    letters_only = [char for char in text_lower if char.isalpha()]

    if not letters_only:
        return {}

    total_letters = len(letters_only)
    letter_counts = Counter(letters_only)

    frequencies = {
        letter: (count / total_letters) * 100
        for letter, count in letter_counts.items()
    }

    return dict(sorted(frequencies.items(), key=lambda x: x[1], reverse=True))

def detect_language(frequencies):
    """
    Определяет язык текста на основе частот букв
    """
    if not frequencies:
        return 'mixed'

    russian_letters = set('абвгдежзийклмнопрстуфхцчшщъыьэюя')
    english_letters = set(string.ascii_lowercase)

    text_letters = set(frequencies.keys())

    has_russian = bool(text_letters & russian_letters)
    has_english = bool(text_letters & english_letters)

    if has_russian and not has_english:
        return 'russian'
    elif has_english and not has_russian:
        return 'english'
    else:
        return 'mixed'

def create_frequency_chart(frequencies):
    """
    Создает столбчатую диаграмму частотного анализа
    """
    if not frequencies:
        return None

    letters = list(frequencies.keys())
    values = list(frequencies.values())

    fig = go.Figure(data=[
        go.Bar(
            x=letters,
            y=values,
            marker_color='#1f77b4',
            text=[f'{v:.2f}%' for v in values],
            textposition='auto',
        )
    ])

    fig.update_layout(
        title='Частотное распределение букв',
        xaxis_title='Буквы',
        yaxis_title='Частота (%)',
        height=400,
        showlegend=False
    )

    return fig.to_html(full_html=False)

def create_comparison_chart(frequencies):
    """
    Создает сравнительную диаграмму частот текста с эталонными частотами
    """
    if not frequencies:
        return None

    language = detect_language(frequencies)

    if language == 'mixed':
        return create_frequency_chart(frequencies)

    reference_freq = RUSSIAN_REFERENCE_FREQ if language == 'russian' else ENGLISH_REFERENCE_FREQ

    all_letters = sorted(set(list(frequencies.keys()) + list(reference_freq.keys())))

    text_values = [frequencies.get(letter, 0) for letter in all_letters]
    ref_values = [reference_freq.get(letter, 0) for letter in all_letters]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=all_letters,
        y=text_values,
        name='Ваш текст',
        marker_color='#1f77b4',
        text=[f'{v:.2f}%' if v > 0 else '' for v in text_values],
        textposition='auto',
    ))

    fig.add_trace(go.Bar(
        x=all_letters,
        y=ref_values,
        name=f'Эталон ({"русский" if language == "russian" else "английский"})',
        marker_color='#ff7f0e',
        text=[f'{v:.2f}%' if v > 0 else '' for v in ref_values],
        textposition='auto',
    ))

    fig.update_layout(
        title=f'Сравнение частот: ваш текст vs эталонные частоты',
        xaxis_title='Буквы',
        yaxis_title='Частота (%)',
        height=500,
        barmode='group',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    return fig.to_html(full_html=False)

# ========== HTML ШАБЛОН ==========

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔐 CryptoLab - Образовательная платформа по криптоанализу</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 30px;
        }
        .controls {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #2c3e50;
        }
        textarea, input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        textarea:focus, input:focus, select:focus {
            border-color: #667eea;
            outline: none;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
            width: 100%;
        }
        button:hover {
            transform: translateY(-2px);
        }
        .result {
            background: #e8f5e8;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            border-left: 5px solid #27ae60;
        }
        .brute-force-result {
            background: #fff3cd;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 5px solid #ffc107;
        }
        .info-box {
            background: #d1ecf1;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 5px solid #17a2b8;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
            color: #6c757d;
        }
        .tab {
            display: none;
        }
        .tab.active {
            display: block;
        }
        .nav-tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 2px solid #e9ecef;
        }
        .nav-tab {
            padding: 12px 24px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 16px;
            border-bottom: 3px solid transparent;
            margin-right: 5px;
        }
        .nav-tab.active {
            border-bottom: 3px solid #667eea;
            color: #667eea;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 CryptoLab - Образовательная платформа по криптоанализу</h1>
        <div class="subtitle">Исследуйте классические шифры и методы их взлома</div>

        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('caesar')">Шифр Цезаря</button>
            <button class="nav-tab" onclick="showTab('vigenere')">Шифр Виженера</button>
            <button class="nav-tab" onclick="showTab('atbash')">Шифр Атбаш</button>
            <button class="nav-tab" onclick="showTab('brute')">Взлом Цезаря</button>
            <button class="nav-tab" onclick="showTab('frequency')">Частотный анализ</button>
        </div>

        <!-- ШИФР ЦЕЗАРЯ -->
        <div id="caesar" class="tab active">
            <div class="controls">
                <form method="POST">
                    <input type="hidden" name="cipher_type" value="caesar">
                    <div class="form-group">
                        <label>Введите текст:</label>
                        <textarea name="text" rows="4" placeholder="Введите текст для шифрования/дешифрования...">{{ request.form.text if request.form.cipher_type == 'caesar' else '' }}</textarea>
                    </div>
                    <div class="form-group">
                        <label>Ключ сдвига:</label>
                        <input type="number" name="shift" value="{{ request.form.shift if request.form.cipher_type == 'caesar' else '3' }}" min="1" max="100">
                    </div>
                    <div class="form-group">
                        <label>Операция:</label>
                        <select name="operation">
                            <option value="encrypt" {% if request.form.get('operation') == 'encrypt' %}selected{% endif %}>Зашифровать</option>
                            <option value="decrypt" {% if request.form.get('operation') == 'decrypt' %}selected{% endif %}>Расшифровать</option>
                        </select>
                    </div>
                    <button type="submit" name="action" value="process">🚀 Выполнить</button>
                </form>
            </div>

            {% if result and request.form.cipher_type == 'caesar' %}
            <div class="result">
                <strong>📤 Результат ({{ "зашифровано" if request.form.operation == "encrypt" else "расшифровано" }}):</strong>
                <pre style="white-space: pre-wrap; background: white; padding: 15px; border-radius: 5px; margin-top: 10px;">{{ result }}</pre>
                <div class="info-box">
                    <strong>ℹ️ Использованный ключ:</strong> {{ request.form.shift }}
                </div>
            </div>
            {% endif %}
        </div>

        <!-- ШИФР ВИЖЕНЕРА -->
        <div id="vigenere" class="tab">
            <div class="controls">
                <form method="POST">
                    <input type="hidden" name="cipher_type" value="vigenere">
                    <div class="form-group">
                        <label>Введите текст:</label>
                        <textarea name="text" rows="4" placeholder="Введите текст для шифрования/дешифрования...">{{ request.form.text if request.form.cipher_type == 'vigenere' else '' }}</textarea>
                    </div>
                    <div class="form-group">
                        <label>Ключевое слово:</label>
                        <input type="text" name="vigenere_key" value="{{ request.form.vigenere_key if request.form.cipher_type == 'vigenere' else 'KEY' }}" placeholder="Введите ключевое слово">
                    </div>
                    <div class="form-group">
                        <label>Операция:</label>
                        <select name="operation">
                            <option value="encrypt" {% if request.form.get('operation') == 'encrypt' %}selected{% endif %}>Зашифровать</option>
                            <option value="decrypt" {% if request.form.get('operation') == 'decrypt' %}selected{% endif %}>Расшифровать</option>
                        </select>
                    </div>
                    <button type="submit" name="action" value="process">🚀 Выполнить</button>
                </form>
            </div>

            {% if result and request.form.cipher_type == 'vigenere' %}
            <div class="result">
                <strong>📤 Результат ({{ "зашифровано" if request.form.operation == "encrypt" else "расшифровано" }}):</strong>
                <pre style="white-space: pre-wrap; background: white; padding: 15px; border-radius: 5px; margin-top: 10px;">{{ result }}</pre>
                <div class="info-box">
                    <strong>ℹ️ Использованное ключевое слово:</strong> {{ request.form.vigenere_key }}
                </div>
            </div>
            {% endif %}
        </div>

        <!-- ШИФР АТБАШ -->
        <div id="atbash" class="tab">
            <div class="controls">
                <form method="POST">
                    <input type="hidden" name="cipher_type" value="atbash">
                    <div class="form-group">
                        <label>Введите текст:</label>
                        <textarea name="text" rows="4" placeholder="Введите текст для преобразования...">{{ request.form.text if request.form.cipher_type == 'atbash' else '' }}</textarea>
                    </div>
                    <button type="submit" name="action" value="process">🚀 Выполнить</button>
                </form>
            </div>

            {% if result and request.form.cipher_type == 'atbash' %}
            <div class="result">
                <strong>📤 Результат:</strong>
                <pre style="white-space: pre-wrap; background: white; padding: 15px; border-radius: 5px; margin-top: 10px;">{{ result }}</pre>
                <div class="info-box">
                    <strong>ℹ️ Примечание:</strong> Шифр Атбаш симметричен - повторное применение вернёт исходный текст
                </div>
            </div>
            {% endif %}
        </div>

        <!-- ВЗЛОМ ЦЕЗАРЯ -->
        <div id="brute" class="tab">
            <div class="controls">
                <form method="POST">
                    <input type="hidden" name="cipher_type" value="brute_force">
                    <div class="form-group">
                        <label>Введите зашифрованный текст:</label>
                        <textarea name="text" rows="4" placeholder="Введите зашифрованный текст для взлома...">{{ request.form.text if request.form.cipher_type == 'brute_force' else '' }}</textarea>
                    </div>
                    <button type="submit" name="action" value="process">🔍 Взломать</button>
                </form>
            </div>

            {% if brute_results and request.form.cipher_type == 'brute_force' %}
            <div class="result">
                <strong>🔓 Результаты взлома:</strong>
                <p>Найдено {{ brute_results|length }} возможных вариантов:</p>
                {% for shift, decrypted, lang in brute_results %}
                <div class="brute-force-result">
                    <strong>Сдвиг {{ shift }} ({{ lang }}):</strong>
                    <pre style="white-space: pre-wrap; background: white; padding: 10px; border-radius: 5px; margin-top: 5px;">{{ decrypted }}</pre>
                </div>
                {% endfor %}
                <div class="info-box">
                    💡 <strong>Подсказка:</strong> Найдите вариант, который имеет смысл!
                </div>
            </div>
            {% endif %}
        </div>

        <!-- ЧАСТОТНЫЙ АНАЛИЗ -->
        <div id="frequency" class="tab">
            <div class="controls">
                <form method="POST">
                    <input type="hidden" name="cipher_type" value="frequency">
                    <div class="form-group">
                        <label>Введите текст для анализа:</label>
                        <textarea name="text" rows="4" placeholder="Введите текст для частотного анализа...">{{ request.form.text if request.form.cipher_type == 'frequency' else '' }}</textarea>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" name="show_comparison" value="true" {% if request.form.get('show_comparison') %}checked{% endif %}>
                            Сравнить с эталонными частотами
                        </label>
                    </div>
                    <button type="submit" name="action" value="process">📊 Анализировать</button>
                </form>
            </div>

            {% if frequency_data and request.form.cipher_type == 'frequency' %}
            <div class="result">
                <strong>📊 Результаты анализа:</strong>
                <div class="info-box">
                    🌐 <strong>Определённый язык:</strong> 
                    {% if frequency_data.language == 'russian' %}русский
                    {% elif frequency_data.language == 'english' %}английский
                    {% else %}смешанный{% endif %}
                </div>

                {% if frequency_data.plot_html %}
                <div style="margin: 20px 0;">
                    {{ frequency_data.plot_html|safe }}
                </div>
                {% endif %}

                <div class="info-box">
                    <strong>🔝 Топ-10 наиболее частых букв:</strong><br>
                    {% for letter, freq in frequency_data.top_10 %}
                    {{ loop.index }}. '{{ letter }}' - {{ "%.2f"|format(freq) }}%<br>
                    {% endfor %}
                </div>

                <div class="info-box">
                    <strong>📈 Статистика:</strong><br>
                    Всего букв: {{ frequency_data.total_letters }}<br>
                    Уникальных букв: {{ frequency_data.unique_letters }}
                </div>
            </div>
            {% endif %}
        </div>

        <div class="footer">
            <p><strong>💡 Образовательная платформа по криптоанализу</strong></p>
            <p>Разработчик: daniilbrusentsov@gmail.com</p>
            <p>Ученик 10-А класса Брусенцов Даниил | Работа для индивидуального проекта</p>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            // Скрыть все табы
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            // Показать выбранный таб
            document.getElementById(tabName).classList.add('active');
            
            // Обновить активную вкладку в навигации
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.classList.add('active');
        }

        // Автоматически показывать таб с результатом после отправки формы
        {% if request.form.cipher_type %}
        document.addEventListener('DOMContentLoaded', function() {
            showTab('{{ request.form.cipher_type }}');
        });
        {% endif %}
    </script>
</body>
</html>
'''

# ========== ОБРАБОТЧИКИ FLASK ==========

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    brute_results = None
    frequency_data = None
    
    if request.method == 'POST' and request.form.get('action') == 'process':
        cipher_type = request.form.get('cipher_type')
        text = request.form.get('text', '')
        
        if cipher_type == 'caesar':
            shift = int(request.form.get('shift', 3))
            operation = request.form.get('operation', 'encrypt')
            result = caesar_cipher(text, shift, operation)
            
        elif cipher_type == 'vigenere':
            key = request.form.get('vigenere_key', '')
            operation = request.form.get('operation', 'encrypt')
            result = vigenere_cipher(text, key, operation)
            
        elif cipher_type == 'atbash':
            result = atbash_cipher(text)
            
        elif cipher_type == 'brute_force':
            brute_results = caesar_brute_force(text)
            
        elif cipher_type == 'frequency':
            frequencies = frequency_analysis(text)
            show_comparison = request.form.get('show_comparison') == 'true'
            
            if frequencies:
                language = detect_language(frequencies)
                
                if show_comparison and language != 'mixed':
                    plot_html = create_comparison_chart(frequencies)
                else:
                    plot_html = create_frequency_chart(frequencies)
                
                top_10 = list(frequencies.items())[:10]
                total_letters = sum(1 for c in text.lower() if c.isalpha())
                unique_letters = len(frequencies)
                
                frequency_data = {
                    'language': language,
                    'plot_html': plot_html,
                    'top_10': top_10,
                    'total_letters': total_letters,
                    'unique_letters': unique_letters
                }
    
    return render_template_string(
        HTML_TEMPLATE, 
        result=result,
        brute_results=brute_results,
        frequency_data=frequency_data,
        request=request
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)