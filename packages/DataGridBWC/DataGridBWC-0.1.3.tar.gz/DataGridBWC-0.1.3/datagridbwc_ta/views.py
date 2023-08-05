from blazeweb.views import View
from sqlalchemybwc import db

from datagridbwc.lib import DataGrid, Col
from datagridbwc_ta.model.orm import Car, Radio

class DataGrid1(View):
    def default(self):
        dg = DataGrid(
            db.sess.execute,
            per_page = 1,
            )
        dg.add_col(
            'id',
            Car.id,
            inresult=True
        )
        #dg.add_tablecol(
        #    Col('Actions',
        #        extractor=self.action_links,
        #        width_th='8%'
        #    ),
        #    orm.CorpEntity.id,
        #    sort=None
        #)
        dg.add_tablecol(
            Col('Make'),
            Car.make,
            filter_on=True,
            sort='both'
        )
        dg.add_tablecol(
            Col('Model'),
            Car.model,
            filter_on=True,
            sort='both'
        )
        dg.add_tablecol(
            Col('Year'),
            Car.year,
            filter_on=True,
            sort='both'
        )
        self.assign('dg', dg)
        self.render_template()

class DataGrid2(View):
    def default(self):
        dg = DataGrid(
            db.sess.execute,
            rs_customizer = lambda q: q.where(Car.radio_id == Radio.id),
            per_page = 1,
            )
        dg.add_col(
            'id',
            Car.id,
            inresult=True
        )
        dg.add_tablecol(
            Col('Make'),
            Car.make,
            filter_on=True,
            sort='both'
        )
        dg.add_tablecol(
            Col('Model'),
            Car.model,
            filter_on=True,
            sort='both'
        )
        dg.add_tablecol(
            Col('Radio'),
            Radio.model.label('radio_model'),
            filter_on=True,
            sort='both'
        )
        self.assign('dg', dg)
        self.render_template()
