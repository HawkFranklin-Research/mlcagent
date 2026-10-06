from textual.widgets import Static


class Subgoals(Static):
    def render_state(self,status):
        event=status['event_spec']
        lines=[event['goal'],'']
        for subgoal in event['subgoals']:
            result=status['subgoals'].get(event['id']+'.'+subgoal['id'],{})
            lines.append(('✓ ' if result.get('passed') else '□ ')+subgoal['id']+': '+subgoal['text'])
        self.update('\n'.join(lines))
