import random
import re

__all__ = ['CPF']

class CPF(object):
    def __init__(self, cpf=None):
        """Create a CPF instance.

        If a string is provided as argument, use it as the CPF number; otherwise, generate a new one.

        If the string provided doesn't contain 11 digits, exactly, raise ValueError.
        """
        if cpf is None:
            cpf = self.gen()
        else:
            cpf = str(cpf)
            cpf = re.sub(r'[^\d]+', '', cpf)

            if len(cpf) is not 11:
                raise ValueError("CPF should contain 11 digits")

            self.cpf = [int(token) for token in cpf]
        return None

    def __eq__(self, other):
        if not isinstance(other, CPF):
            other = CPF(other)
        return self.cpf == other.cpf

    def __genNumber__(self):
        trial_digits = [random.randint(0, 9) for i in range(0, 11)]
        return trial_digits

    def __getitem__(self, index):
        return str(self.cpf[index])

    def __int__(self):
        return int(''.join([str(x) for x in self.cpf]))

    def __repr__(self):
        return "CPF('%s')" % ''.join([str(x) for x in self.cpf])

    def __str__(self):
        d = ((3, "."), (7, "."), (11, "-"))
        s = [str(token) for token in self.cpf]

        for i, v in d:
            s.insert(i,v)

        return ''.join(s)

    def gen(self, __return__=False):
        self.cpf = self.__genNumber__()

        while self.valid() == False:
            self.cpf = self.__genNumber__()
        return (True, self.cpf)[__return__]

    def valid(self):
        c = self.cpf[:9]
        p = [10, 9, 8, 7, 6, 5, 4, 3, 2]

        while len(c) < 11:
            t = sum([x * y for (x, y) in zip(c, p)]) % 11
            c.append((0, 11 - t)[t >= 2])
            p.insert(0, 11)
        return bool(c == self.cpf)

