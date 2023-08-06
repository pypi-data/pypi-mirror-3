from protocol import State, Vector, Segment, Buffer, Insert, Delete, UndoRequest, DoRequest


class InfinoteDocument(object):
    
    def __init__(self):
        self.log = []
        self._state = State()

    def try_insert(self, params):
        #user, text
        segment = Segment(params[0], params[3])
        buffer = Buffer([segment])
        #position, buffer
        operation = Insert(params[2], buffer)
        #user, vector
        request = DoRequest(params[0], Vector(params[1]), operation)
        if self._state.canExecute(request):
            executedRequest = self._state.execute(request)
            self.log.append(["i",tuple(params)])        

    def try_delete(self, params):
        operation = Delete(params[2], params[3])
        #user, vector, operation
        request = DoRequest(params[0], Vector(params[1]), operation)
        if self._state.canExecute(request):
            executedRequest = self._state.execute(request) 
            self.log.append(["d",tuple(params)])        
        
    def try_undo(self, params):
        request = UndoRequest(params[0], self._state.vector)
        if self._state.canExecute(request):
            executedRequest = self._state.execute(request)
            self.log.append(["u",tuple(params)])        
            
    def sync(self):
        for log in self.log:
            if log[0] == 'i': 
                self.try_insert(log[1])
            elif log[0] =='d':
                self.try_delete(log[1])
            elif log[0] == 'u':
                self.try_undo(log[1])                
                
    def get_state(self):
        return (self._state.vector.toString(), self._state.buffer.toString())         
    
    def get_log(self, limit = None):
        if limit != None:
            if len(self.log) >=limit:
                return (limit, self.log[-limit:])
            else:
                return (limit, self.log)
        else:
            return (limit, self.log)