#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Scenario tests for Retention mode to validate branching and anti-loop behavior.
"""
from backend.app.services.gpt_service import generate_question


def _append(conv, qdict, answer_text):
    conv.append({
        "question": qdict.get('question'),
        "goal": qdict.get('goal'),
        "answer": answer_text,
    })


def run_until_closing(mode, conv, max_steps=20):
    steps = []
    for _ in range(max_steps):
        q = generate_question(mode, conv)
        steps.append((q.get('goal'), q.get('question')))
        if q.get('is_closing'):
            return q, steps
        # Caller must append answer for next loop
        return q, steps
    return None, steps


def scenario_wrong_number_close():
    print("\n=== Scenario 1: Wrong number -> close ===")
    conv = []
    # Greeting
    conv.append({
        "question": "Halo, saya dari ICONNET. Apakah benar terhubung dengan Bapak/Ibu?",
        "answer": "Bukan saya"
    })
    q1 = generate_question('retention', conv)
    # Answer: nomor salah/owner tidak ada -> expect closing next
    _append(conv, q1, "Nomor salah")
    q2 = generate_question('retention', conv)
    print("Next Goal:", q2.get('goal'), "| Is Closing:", q2.get('is_closing'))
    return q2.get('is_closing') is True


def scenario_wrong_number_then_owner():
    print("\n=== Scenario 2: Wrong number then owner present -> service_check path ===")
    conv = []
    conv.append({
        "question": "Halo, saya dari ICONNET. Apakah benar terhubung dengan Bapak/Ibu?",
        "answer": "Bukan saya"
    })
    q1 = generate_question('retention', conv)
    _append(conv, q1, "Saya pemiliknya")
    q2 = generate_question('retention', conv)
    print("Next Goal:", q2.get('goal'))
    return q2.get('goal') == 'service_check'


def scenario_decline_promo_reason_moved():
    print("\n=== Scenario 3: Decline promo -> rejection_reason: moved -> device_location -> relocation_interest -> closing ===")
    conv = []
    conv.append({"question": "Halo", "answer": "Ya, benar"})
    q0 = generate_question('retention', conv)
    _append(conv, q0, "Ya, terputus")  # service_check
    q1 = generate_question('retention', conv)
    _append(conv, q1, "Tidak usah")  # promo_permission declined
    q2 = generate_question('retention', conv)
    _append(conv, q2, "Pindah")  # rejection_reason
    q3 = generate_question('retention', conv)
    _append(conv, q3, "Masih ada")  # device_location
    q4 = generate_question('retention', conv)
    _append(conv, q4, "Tidak berminat")  # relocation_interest
    q5 = generate_question('retention', conv)
    print("Next Goal:", q5.get('goal'), "| Is Closing:", q5.get('is_closing'))
    return q5.get('is_closing') is True or q5.get('goal') == 'closing'


def scenario_decline_then_complaint_resolve_yes():
    print("\n=== Scenario 4: Decline promo -> complaint -> resolution willing -> payment -> closing ===")
    conv = []
    conv.append({"question": "Halo", "answer": "Ya, benar"})
    q0 = generate_question('retention', conv)
    _append(conv, q0, "Ya, terputus")  # service_check
    q1 = generate_question('retention', conv)
    _append(conv, q1, "Tidak usah")  # promo_permission declined
    q2 = generate_question('retention', conv)
    _append(conv, q2, "Ada keluhan")  # rejection_reason
    q3 = generate_question('retention', conv)
    _append(conv, q3, "Sudah pernah")  # complaint_handling
    q4 = generate_question('retention', conv)
    _append(conv, q4, "Lambat")  # complaint_resolution detail
    q5 = generate_question('retention', conv)
    _append(conv, q5, "Bersedia")  # willing to continue
    q6 = generate_question('retention', conv)
    _append(conv, q6, "Ya, aktif")  # payment_confirmation follow-up
    q7 = generate_question('retention', conv)
    _append(conv, q7, "Besok")  # payment_timing
    q8 = generate_question('retention', conv)
    print("Next Goal:", q8.get('goal'), "| Is Closing:", q8.get('is_closing'))
    return q8.get('is_closing') is True or q8.get('goal') == 'closing'


def scenario_consideration():
    print("\n=== Scenario 5: Consideration -> consideration_timeline -> closing ===")
    conv = []
    conv.append({"question": "Halo", "answer": "Ya, benar"})
    q0 = generate_question('retention', conv)
    _append(conv, q0, "Ya, terputus")  # service_check
    q1 = generate_question('retention', conv)
    _append(conv, q1, "Boleh")  # promo_permission
    q2 = generate_question('retention', conv)
    _append(conv, q2, "Oke")  # promo_detail ack
    q3 = generate_question('retention', conv)
    _append(conv, q3, "Pertimbangkan dulu")  # activation_interest consider
    q4 = generate_question('retention', conv)
    _append(conv, q4, "Minggu ini")  # consideration_timeline
    q5 = generate_question('retention', conv)
    print("Next Goal:", q5.get('goal'), "| Is Closing:", q5.get('is_closing'))
    return q5.get('is_closing') is True or q5.get('goal') == 'closing'


def scenario_stop_confirmation():
    print("\n=== Scenario 6: Stop -> stop_confirmation -> closing ===")
    conv = []
    conv.append({"question": "Halo", "answer": "Ya, benar"})
    q0 = generate_question('retention', conv)
    _append(conv, q0, "Ya, terputus")  # service_check
    q1 = generate_question('retention', conv)
    _append(conv, q1, "Boleh")  # promo_permission
    q2 = generate_question('retention', conv)
    _append(conv, q2, "Oke")  # promo_permission / promo_detail ack
    # Ensure promo_detail is asked and answered before activation_interest
    q3 = generate_question('retention', conv)
    _append(conv, q3, "Oke")  # promo_detail ack (confirming details)
    q4 = generate_question('retention', conv)
    _append(conv, q4, "Berhenti")  # activation_interest stop
    q5 = generate_question('retention', conv)
    _append(conv, q5, "Ya, yakin")  # stop_confirmation
    q6 = generate_question('retention', conv)
    print("Next Goal:", q5.get('goal'), "| Is Closing:", q5.get('is_closing'))
    # q6 is the follow-up after stop confirmation; ensure it's closing
    print("Final Next Goal:", q6.get('goal'), "| Is Closing:", q6.get('is_closing'))
    return q6.get('is_closing') is True or q6.get('goal') == 'closing'


if __name__ == '__main__':
    results = {
        'wrong_number_close': scenario_wrong_number_close(),
        'wrong_number_then_owner': scenario_wrong_number_then_owner(),
        'decline_promo_moved': scenario_decline_promo_reason_moved(),
        'decline_then_complaint_resolve_yes': scenario_decline_then_complaint_resolve_yes(),
        'consideration': scenario_consideration(),
        'stop_confirmation': scenario_stop_confirmation(),
    }
    print("\nRESULTS:")
    for k, v in results.items():
        print(f"  {k}: {'PASS' if v else 'FAIL'}")
