#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# Centro de Tecnologías Emergentes del Ejército de Tierra (CTEET)
# Prueba de concepto: Assistant para InSTT
# Created on Tue Feb 15 18:50:00 2024
# @Author: Francisco Jose Ochando Terreros
# @Test: Antonio Mejías Vello, Alejandro Gomez Sierra 
# @Debugging: Francisco Jose Ochando Terreros
#-------------------------------------------------------------------------

import openai


prompt = ''
respuesta = ''
engine = "gpt-3.5-turbo-instruct"
#engine = "mistral-7b-instruct-v0.1.Q4_0"
openai.apikey = "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"
max_tokens = 200
temperature = 0.2
top_p = 0.95
n = 1
echo = True
stream = False

def Completion(miprompt):
    openai.apikey = "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"
    response = openai.Completion.create(
        model= engine,
        prompt= miprompt,
        max_tokens= max_tokens,
        temperature= temperature,
        top_p= top_p,
        n= n,
        echo= echo,
        stream= stream
    )
    cadena = response.choices[-1].text.strip()
    print(cadena)
    return cadena

def Chat_completion(miprompt):
    openai.apikey = "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"
    messages = [{"role": "assistant", "content": "Buenos días "}]
    messages.append({"role": "user", "content": miprompt})
    response = openai.ChatCompletion.create(
        model= engine,
        messages=[{"role": m["role"], "content": m["content"]} for m in messages],
        temperature= temperature
    )
    messages.append({"role": "assistant", "content": response})
    print(f"Máquina: {response.choices[0].message.content}")
    cadena = response.choices[0].message.content
    return cadena

if __name__ == "__main__":

    respuesta = Completion('Hola TARS!')
    print(respuesta)