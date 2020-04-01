package dev.miramontes.spaghetti.ui.saving

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.TextView
import dev.miramontes.spaghetti.R
import dev.miramontes.spaghetti.library.generateDebugName
import dev.miramontes.spaghetti.library.generateDebugSpaghettiString

class SavingsListAdapter(ctx: Context) : BaseAdapter() {
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
        val rowView = inflater.inflate(R.layout.activity_savings_list, parent, false)
        val accountNameView: TextView = rowView.findViewById(R.id.account_name)
        accountNameView.text = generateDebugName()

        val balanceView: TextView = rowView.findViewById(R.id.balance)
        balanceView.text =
            generateDebugSpaghettiString()
        return rowView
    }
}