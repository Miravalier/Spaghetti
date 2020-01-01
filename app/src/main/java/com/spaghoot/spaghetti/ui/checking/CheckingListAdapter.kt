package com.spaghoot.spaghetti.ui.checking

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.TextView
import com.spaghoot.spaghetti.R
import kotlin.random.Random

class CheckingListAdapter(ctx: Context) : BaseAdapter() {
    private val inflater: LayoutInflater
            = ctx.getSystemService(Context.LAYOUT_INFLATER_SERVICE) as LayoutInflater

    override fun getCount(): Int {
        return 5
    }

    override fun getItem(position: Int): Any {
        return position
    }

    override fun getItemId(position: Int): Long {
        return position.toLong()
    }

    override fun getView(position: Int, convertView: View?, parent: ViewGroup?): View {
        val rowView = inflater.inflate(R.layout.activity_checking_list, parent, false)
        val loanNameView: TextView = rowView.findViewById(R.id.account_name)
        loanNameView.text = String.format("Test %d", Random.nextInt())
        val amountOwedView: TextView = rowView.findViewById(R.id.balance)
        amountOwedView.text = String.format("%.3f sp", Random.nextDouble(1000.0))
        return rowView
    }
}