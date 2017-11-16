import execjs

js_text = open('main.js', 'r', encoding='utf8').read()
js = execjs.compile(js_text)
result = js.call("encryptedString", "123456789hhs")
print(result)
