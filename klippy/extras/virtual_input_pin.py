from pyparsing import *

import klippy

class VirtualInputPin:
    def __init__(self, formula, pins):
        self.formula = formula
        self.pins = pins

    def get_state(self):
        x_list = [Symbol(f'x{i}') for i in range(len(self.pins))]
        state = self.formula.subs(zip(x_list,
                                      [pin.get_state() for pin in self.pins]))
        return state

def get_mcu(mcu_id, formula, *pins_params):
    if mcu_id == 'custom_formula_pin':
        try:
            mcu_pin_list = []
            for pin in pins_params:
                pin_mcu, pin_name = pin.split(':')
                mcu = klippy.get_mcu(pin_mcu)
                mcu_pin_list.append(mcu.get_pin(pin_name))
            and_ = CaselessKeyword("and")
            or_ = CaselessKeyword("or")
            not_ = CaselessKeyword("not")
            lpar = Literal("(").suppress()
            rpar = Literal(")").suppress()
            x_list = [Symbol(f'x{i}') for i in range(len(pins_params))]
            expr = operatorPrecedence( x_list[0],
                [
                (not_, 1, opAssoc.RIGHT),
                ("not", 1, opAssoc.RIGHT),
                (and_, 2, opAssoc.LEFT),
                ("and", 2, opAssoc.LEFT),
                (or_, 2, opAssoc.LEFT),
                ("or", 2, opAssoc.LEFT)
                ])

            # Adding parantheses support
            expr = expr | ( lpar + expr + rpar )

            parsed_formula = expr.parseString(formula, parseAll=True)[0]
            return VirtualInputPin(parsed_formula, mcu_pin_list)
        except Exception as e:
            raise ValueError(f"error occured in formula parsing: {e}")

def load_config(config):
    formula = config.get('formula', '0')
    pins = config.get('pins', [])
    klippy.register_virtual_pin('custom_formula_pin',
                                'custom_formula_pin',
                                get_mcu,
                                formula,
                                *pins)
