"""Local progress and bounded undo. Saves never include runtime or credentials."""
import copy
import json
import os
from pathlib import Path

class Progress:
    def __init__(self,path=None):
        self.path=Path(path or os.environ.get('SHELLBOUND_SAVE_PATH') or
                       Path(__file__).resolve().parent.parent/'.cache'/'progress-v2.json')
        self.highest=2  # The first three rooms were already freely selectable.
        self.records={}
        self.muted=False;self.shake=True;self.error=None
        try:
            data=json.loads(self.path.read_text(encoding='utf-8'))
            if data.get('version')!=2:return
            self.highest=max(2,min(7,int(data.get('highest',2))))
            self.muted=bool(data.get('muted',False));self.shake=bool(data.get('shake',True))
            for key,r in data.get('records',{}).items():
                index=int(key)
                if index not in range(8) or not isinstance(r,dict):continue
                time=float(r.get('time',0));stars=int(r.get('stars',1))
                if 0<time<86400:self.records[index]={'time':time,'stars':max(1,min(3,stars))}
        except (OSError,ValueError,TypeError,AttributeError):pass

    @property
    def finished(self):return 7 in self.records

    @property
    def next_stage(self):
        for i in range(8):
            if i not in self.records:return min(i,self.highest)
        return 7

    def complete(self,world):
        if world.result!='clear' or world.used_practice or world.practice:return False
        index=world.stage_index
        stars=1+int(world.hp==5)+int(world.stats['bodies_lost']==0)
        previous=self.records.get(index)
        self.records[index]={'time':round(min(world.time,previous['time']) if previous else world.time,2),
                             'stars':max(stars,previous['stars']) if previous else stars}
        self.highest=max(self.highest,min(7,index+1))
        self.save();return True

    def save(self):
        data={'version':2,'highest':self.highest,'records':self.records,'muted':self.muted,'shake':self.shake}
        try:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            temporary=self.path.with_suffix('.tmp')
            temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
            os.replace(temporary,self.path)
            self.error=None
        except OSError as exc:self.error=type(exc).__name__

class Undo:
    def __init__(self):self.items=[]
    def take(self,world):
        self.items.append(copy.deepcopy(world))
        self.items=self.items[-32:]
    def restore(self):return self.items.pop() if self.items else None
