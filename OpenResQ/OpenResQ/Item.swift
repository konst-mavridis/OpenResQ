//
//  Item.swift
//  OpenResQ
//
//  Created by Konstantinos Mavridis on 18/3/26.
//

import Foundation
import SwiftData

@Model
final class Item {
    var timestamp: Date
    
    init(timestamp: Date) {
        self.timestamp = timestamp
    }
}
